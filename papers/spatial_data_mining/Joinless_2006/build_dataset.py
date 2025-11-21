import pandas as pd
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import pickle
import os
from pathlib import Path


# 1. INSTANCE DATA STRUCTURE
@dataclass
class SpatialInstance:
    """
    Represents a single instance (location point) in the dataset.
    Maps to one row in your CSV.
    """

    feature: str  # Feature type (e.g., 'A', 'B', 'C')
    instance_id: int  # Unique instance ID within the feature
    x: float  # LocX coordinate
    y: float  # LocY coordinate
    checkin: int  # Check-in count (popularity measure)

    def __hash__(self):
        return hash((self.feature, self.instance_id))

    def __eq__(self, other):
        return self.feature == other.feature and self.instance_id == other.instance_id

    def distance_to(self, other: "SpatialInstance") -> float:
        """Calculate Euclidean distance to another instance."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


# 2. FEATURE DATA STRUCTURE
@dataclass
class Feature:
    """
    Represents a feature type and all its instances.
    Example: Feature 'A' contains all instances of type 'A'.
    """

    name: str  # Feature name (e.g., 'A')
    instances: List[SpatialInstance] = field(default_factory=list)

    def get_instance_count(self) -> int:
        """Return number of instances of this feature."""
        return len(self.instances)


# 3. NEIGHBOR RELATIONSHIP (for Joinless Algorithm)
@dataclass
class NeighborRelation:
    """
    Represents a spatial neighbor relationship between two instances.
    Used to build star neighborhoods and cliques.
    """

    instance1: SpatialInstance
    instance2: SpatialInstance
    distance: float  # Euclidean distance between them

    def __hash__(self):
        # Make it unordered (instance1, instance2) = (instance2, instance1)
        pair = tuple(
            sorted(
                [
                    (self.instance1.feature, self.instance1.instance_id),
                    (self.instance2.feature, self.instance2.instance_id),
                ]
            )
        )
        return hash(pair)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


# 4. STAR NEIGHBORHOOD (Joinless Algorithm Core Structure)
@dataclass
class StarNeighborhood:
    """
    Represents a star neighborhood centered at an instance.
    In joinless algorithm, each instance has a star of neighbors.
    Key structure: instance -> set of neighboring instances
    """

    center_instance: SpatialInstance  # The center instance
    neighbors: List[SpatialInstance] = field(default_factory=list)

    def add_neighbor(self, neighbor: SpatialInstance):
        """Add a neighbor to the star."""
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)

    def get_feature_types(self) -> Set[str]:
        """Get set of feature types in this star neighborhood."""
        return {inst.feature for inst in self.neighbors}


# 5. CLIQUE DATA STRUCTURE
@dataclass
class Clique:
    """
    Represents a clique - a set of instances where every pair is neighbors.
    In co-location pattern mining, cliques represent co-location instances.
    """

    instances: List[SpatialInstance] = field(default_factory=list)

    def __hash__(self):
        # Sort instances for consistent hashing
        sorted_instances = tuple(
            sorted([(inst.feature, inst.instance_id) for inst in self.instances])
        )
        return hash(sorted_instances)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def get_feature_pattern(self) -> Tuple[str, ...]:
        """Get the feature pattern (set of feature types) in this clique."""
        return tuple(sorted(set(inst.feature for inst in self.instances)))

    def size(self) -> int:
        """Return number of instances in clique."""
        return len(self.instances)


# 6. CO-LOCATION PATTERN DATA STRUCTURE
@dataclass
class ColocationPattern:
    """
    Represents a co-location pattern (set of feature types that co-occur).
    Example: Pattern {A, B, C} means features A, B, C are frequently together.
    """

    features: Tuple[str, ...]  # Sorted tuple of feature names
    cliques: List[Clique] = field(
        default_factory=list
    )  # All cliques supporting this pattern

    def __hash__(self):
        return hash(self.features)

    def __eq__(self, other):
        return self.features == other.features

    def get_prevalence_index(self) -> Dict[str, float]:
        """
        Calculate prevalence index (participation index) for each feature.
        Returns: Dict mapping feature -> participation ratio
        """
        if not self.cliques:
            return {}

        prevalence = {}
        for feature in self.features:
            # Count unique instances of this feature in all cliques
            unique_instances = set()
            for clique in self.cliques:
                for inst in clique.instances:
                    if inst.feature == feature:
                        unique_instances.add((inst.feature, inst.instance_id))

            # Get total instances of this feature (need to pass total count)
            # This would be calculated externally
            prevalence[feature] = len(unique_instances)

        return prevalence

    def participation_ratio(
        self, feature: str, total_instances: Dict[str, int]
    ) -> float:
        """
        Calculate participation ratio for a specific feature.
        participation_ratio = (instances of feature in pattern) / (total instances of feature)
        """
        if feature not in self.features or not self.cliques:
            return 0.0

        # Count unique instances of this feature in pattern cliques
        pattern_instances = set()
        for clique in self.cliques:
            for inst in clique.instances:
                if inst.feature == feature:
                    pattern_instances.add((inst.feature, inst.instance_id))

        total = total_instances.get(feature, 1)
        return len(pattern_instances) / total if total > 0 else 0.0

    def participation_index(self, total_instances: Dict[str, int]) -> float:
        """
        Calculate participation index of the pattern.
        PI = min(participation_ratio(f) for f in features)
        """
        if not self.features:
            return 0.0

        ratios = [self.participation_ratio(f, total_instances) for f in self.features]
        return min(ratios) if ratios else 0.0


# 7. MAIN DATA CONTAINER
@dataclass
class SpatialDataset:
    """
    Main container for all spatial data and structures.
    This is the primary object you'll work with.
    """

    instances: List[SpatialInstance] = field(default_factory=list)
    features: Dict[str, Feature] = field(default_factory=dict)
    neighbor_relations: Set[NeighborRelation] = field(default_factory=set)
    star_neighborhoods: Dict[SpatialInstance, StarNeighborhood] = field(
        default_factory=dict
    )
    distance_threshold: float = 0.0  # Will be set when building neighbors

    def add_instance(self, instance: SpatialInstance):
        """Add an instance and organize by feature."""
        self.instances.append(instance)

        if instance.feature not in self.features:
            self.features[instance.feature] = Feature(name=instance.feature)

        self.features[instance.feature].instances.append(instance)

    def get_feature_instance_count(self, feature: str) -> int:
        """Get total number of instances for a feature."""
        return len(self.features.get(feature, Feature(name=feature)).instances)

    def build_neighbor_relations(self, threshold: float):
        """
        Build neighbor relations based on distance threshold.
        This creates the spatial neighborhood graph.
        """
        self.distance_threshold = threshold
        self.neighbor_relations.clear()

        for i, inst1 in enumerate(self.instances):
            for inst2 in self.instances[i + 1 :]:
                distance = inst1.distance_to(inst2)
                if distance <= threshold:
                    relation = NeighborRelation(inst1, inst2, distance)
                    self.neighbor_relations.add(relation)

    def build_star_neighborhoods(self):
        """
        Build star neighborhoods for joinless algorithm.
        Each instance becomes a center with its neighbors.
        """
        self.star_neighborhoods.clear()

        for instance in self.instances:
            star = StarNeighborhood(center_instance=instance)
            self.star_neighborhoods[instance] = star

        # Populate neighbors from neighbor relations
        for relation in self.neighbor_relations:
            center = relation.instance1
            neighbor = relation.instance2

            if center in self.star_neighborhoods:
                self.star_neighborhoods[center].add_neighbor(neighbor)

            # Also add reverse (bidirectional)
            if neighbor in self.star_neighborhoods:
                self.star_neighborhoods[neighbor].add_neighbor(center)

    def save_to_file(self, filepath: str):
        """
        Save the entire dataset (including star neighborhoods) to a pickle file.
        This allows you to load it later without recomputing.
        """
        with open(filepath, "wb") as f:
            pickle.dump(self, f)
        print(f"Dataset saved to {filepath}")

    @staticmethod
    def load_from_file(filepath: str) -> "SpatialDataset":
        """
        Load a previously saved dataset from a pickle file.
        Returns: SpatialDataset with all precomputed structures.
        """
        with open(filepath, "rb") as f:
            dataset = pickle.load(f)
        print(f"Dataset loaded from {filepath}")
        return dataset


# 8. HELPER FUNCTION: Load Dataset from CSV
def load_spatial_dataset(csv_path: str) -> SpatialDataset:
    """
    Load the LasVegas dataset from CSV into SpatialDataset structure.
    """
    df = pd.read_csv(csv_path)
    dataset = SpatialDataset()

    for _, row in df.iterrows():
        instance = SpatialInstance(
            feature=str(row["Feature"]),
            instance_id=int(row["Instance"]),
            x=float(row["LocX"]),
            y=float(row["LocY"]),
            checkin=int(row["Checkin"]),
        )
        dataset.add_instance(instance)

    return dataset


def load_or_build_dataset(
    csv_path: str,
    cache_path: str,
    distance_threshold: float,
    force_rebuild: bool = False,
) -> SpatialDataset:
    """
    Load dataset from cache if available, otherwise build from CSV.

    Args:
        csv_path: Path to CSV file
        cache_path: Path to pickle cache file
        distance_threshold: Distance threshold for neighbor relations
        force_rebuild: If True, rebuild even if cache exists

    Returns:
        SpatialDataset with precomputed star neighborhoods
    """
    if not force_rebuild and os.path.exists(cache_path):
        print("Loading from cache...")
        dataset = SpatialDataset.load_from_file(cache_path)

        # Check if threshold matches
        if dataset.distance_threshold == distance_threshold:
            print(
                f"Loaded {len(dataset.instances)} instances, {len(dataset.star_neighborhoods)} star neighborhoods"
            )
            return dataset
        else:
            print(
                f"Threshold mismatch. Rebuilding with threshold={distance_threshold}..."
            )

    print("Building dataset from CSV...")
    dataset = load_spatial_dataset(csv_path)
    dataset.build_neighbor_relations(threshold=distance_threshold)
    dataset.build_star_neighborhoods()
    dataset.save_to_file(cache_path)
    print("Dataset cached successfully.")
    return dataset


if __name__ == "__main__":
    csv_path = "/media/thuc/9901/0.FALL2025/DBM301m/academic-paper-implementations/data/LasVegas_x_y_alphabet_version_03_2.csv"
    cache_path = "/media/thuc/9901/0.FALL2025/DBM301m/academic-paper-implementations/papers/Joinless/LasVegas_cache.pkl"

    dataset = load_or_build_dataset(csv_path, cache_path, distance_threshold=160.0)
