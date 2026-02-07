# pylint: disable=import-error

import os

import pytest
import utest  # pylint: disable=unused-import

from microzarr import Axis, Zarr, ZarrError, binary_search

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def zarr_path():
    """Path to test Zarr dataset."""
    return "/home/ecastro/aero/devdata/dem.zarr"


@pytest.fixture
def zarr_dataset(zarr_path):
    """Load test Zarr dataset if available."""
    if os.path.exists(zarr_path):  # type: ignore
        return Zarr(zarr_path)
    return None


# ============================================================================
# Test Zarr Initialization
# ============================================================================


class TestZarrInitialization:
    """Test Zarr class initialization and error handling."""

    def test_valid_initialization(self, zarr_dataset):
        """Test initialization with valid Zarr dataset."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        assert zarr_dataset is not None
        assert zarr_dataset.path == "/home/ecastro/aero/devdata/dem.zarr"
        assert zarr_dataset.main_group is not None
        assert zarr_dataset.chunk_height > 0
        assert zarr_dataset.chunk_width > 0
        assert zarr_dataset.x_axis is not None
        assert zarr_dataset.y_axis is not None
        assert zarr_dataset.data is not None

    def test_initialization_sets_attributes(self, zarr_dataset):
        """Test that initialization sets all required attributes."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        required_attrs = ["path", "main_group", "chunk_height", "chunk_width", "x_axis", "y_axis", "data", "data_xy"]
        for attr in required_attrs:
            assert hasattr(zarr_dataset, attr), f"Missing attribute: {attr}"

    def test_chunk_dimensions_extracted(self, zarr_dataset):
        """Test that chunk dimensions are correctly extracted."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        assert isinstance(zarr_dataset.chunk_height, int)
        assert isinstance(zarr_dataset.chunk_width, int)
        assert zarr_dataset.chunk_height > 0
        assert zarr_dataset.chunk_width > 0

    def test_data_buffer_preallocated(self, zarr_dataset):
        """Test that data buffer is preallocated correctly."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        expected_size = zarr_dataset.chunk_height * zarr_dataset.chunk_width * 2
        assert len(zarr_dataset.data) == expected_size


# ============================================================================
# Test Zarr Coordinate Mapping
# ============================================================================


class TestZarrCoordinateMapping:
    """Test coordinate to index mapping functions."""

    def test_loc_at_returns_row_column(self, zarr_dataset):
        """Test that loc_at returns valid row and column indices."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        row, col = zarr_dataset.loc_at(x=0.0, y=49.0)
        assert isinstance(row, int)
        assert isinstance(col, int)
        assert row >= 0
        assert col >= 0

    def test_chunk_at_returns_chunk_ids(self, zarr_dataset):
        """Test that chunk_at returns valid chunk IDs."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        chunk_id_x, chunk_id_y = zarr_dataset.chunk_at(x=0.0, y=49.0)
        assert isinstance(chunk_id_x, int)
        assert isinstance(chunk_id_y, int)
        assert chunk_id_x >= 0
        assert chunk_id_y >= 0

    def test_same_chunk_for_nearby_coordinates(self, zarr_dataset):
        """Test that nearby coordinates return same chunk ID."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        chunk1 = zarr_dataset.chunk_at(x=0.0, y=49.0)
        chunk2 = zarr_dataset.chunk_at(x=0.01, y=49.01)
        assert chunk1 == chunk2

    def test_different_chunks_for_distant_coordinates(self, zarr_dataset):
        """Test that distant coordinates return different chunk IDs."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        chunk1 = zarr_dataset.chunk_at(x=0.0, y=49.0)
        x_step = (zarr_dataset.chunk_width + 10) / 111320.0
        chunk2 = zarr_dataset.chunk_at(x=0.0 + x_step, y=49.0)
        assert chunk1 != chunk2

    def test_chunk_info_boundaries(self, zarr_dataset):
        """Test that chunk_info returns correct boundaries."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        chunk_min_x, chunk_min_y, chunk_max_x, chunk_max_y = zarr_dataset.chunk_info(0, 0)
        assert chunk_min_x == 0
        assert chunk_min_y == 0
        assert chunk_max_x == zarr_dataset.chunk_width - 1
        assert chunk_max_y == zarr_dataset.chunk_height - 1

    def test_chunk_info_for_nonzero_chunk(self, zarr_dataset):
        """Test chunk_info for non-zero chunk ID."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        chunk_min_x, chunk_min_y, chunk_max_x, chunk_max_y = zarr_dataset.chunk_info(1, 1)
        assert chunk_min_x == 1 * zarr_dataset.chunk_width
        assert chunk_min_y == 1 * zarr_dataset.chunk_height
        assert chunk_max_x == 1 * zarr_dataset.chunk_width + zarr_dataset.chunk_width - 1
        assert chunk_max_y == 1 * zarr_dataset.chunk_height + zarr_dataset.chunk_height - 1


# ============================================================================
# Test Zarr Data Retrieval
# ============================================================================


class TestZarrDataRetrieval:
    """Test data retrieval and caching behavior."""

    def test_value_at_returns_int(self, zarr_dataset):
        """Test that value_at returns an integer."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        value = zarr_dataset.value_at(x=0.0, y=49.0)
        assert isinstance(value, int)

    def test_value_at_multiple_coordinates(self, zarr_dataset):
        """Test retrieving values at multiple coordinates."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        values = []
        for offset in [0.0, 0.05, 0.1]:
            value = zarr_dataset.value_at(x=0.0 + offset, y=49.0)
            values.append(value)

        assert len(values) == 3
        for v in values:
            assert isinstance(v, int)

    def test_chunk_loading_caching(self, zarr_dataset):
        """Test that chunk is loaded and cached."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        value1 = zarr_dataset.value_at(x=0.0, y=49.0)
        loaded_chunk = zarr_dataset.data_xy
        value2 = zarr_dataset.value_at(x=0.01, y=49.01)
        assert zarr_dataset.data_xy == loaded_chunk

    def test_chunk_reload_on_different_chunk(self, zarr_dataset):
        """Test that different chunk triggers reload."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        value1 = zarr_dataset.value_at(x=0.0, y=49.0)
        chunk1 = zarr_dataset.data_xy
        x_step = (zarr_dataset.chunk_width + 1) / 111320.0
        value2 = zarr_dataset.value_at(x=0.0 + x_step, y=49.0)
        chunk2 = zarr_dataset.data_xy
        assert chunk1 != chunk2

    def test_data_xy_tracks_current_chunk(self, zarr_dataset):
        """Test that data_xy tracks the currently loaded chunk."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        assert zarr_dataset.data_xy == (None, None)
        value = zarr_dataset.value_at(x=0.0, y=49.0)
        chunk_id_x, chunk_id_y = zarr_dataset.chunk_at(x=0.0, y=49.0)
        assert zarr_dataset.data_xy == (chunk_id_x, chunk_id_y)


# ============================================================================
# Test Axis Class
# ============================================================================


class TestAxisClass:
    """Test Axis class for coordinate mapping."""

    def test_axis_initialization(self, zarr_dataset):
        """Test that Axis initializes correctly."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        assert zarr_dataset.x_axis is not None
        assert zarr_dataset.y_axis is not None
        assert hasattr(zarr_dataset.x_axis, "data_file")
        assert hasattr(zarr_dataset.x_axis, "data_size")
        assert hasattr(zarr_dataset.x_axis, "standard_orientation")

    def test_axis_to_idx_returns_valid_index(self, zarr_dataset):
        """Test that to_idx returns valid index."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        idx = zarr_dataset.x_axis.to_idx(target_value=0.0)
        assert isinstance(idx, int)
        assert 0 <= idx < zarr_dataset.x_axis.data_size

    def test_axis_to_idx_first_value(self, zarr_dataset):
        """Test to_idx with first coordinate value."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        first_val = zarr_dataset.x_axis.first
        idx = zarr_dataset.x_axis.to_idx(target_value=first_val)
        assert idx == 0

    def test_axis_to_idx_last_value(self, zarr_dataset):
        """Test to_idx with last coordinate value."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        last_val = zarr_dataset.x_axis.last
        idx = zarr_dataset.x_axis.to_idx(target_value=last_val)
        assert idx == zarr_dataset.x_axis.data_size - 1

    def test_axis_standard_orientation_flag(self, zarr_dataset):
        """Test that standard_orientation flag is set correctly."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        assert isinstance(zarr_dataset.x_axis.standard_orientation, bool)
        assert isinstance(zarr_dataset.y_axis.standard_orientation, bool)

    def test_axis_cache_mechanism(self, zarr_dataset):
        """Test axis caching behavior."""
        if zarr_dataset is None:
            pytest.skip("Zarr dataset not available")

        idx1 = zarr_dataset.x_axis.to_idx(target_value=0.0)
        cache1 = zarr_dataset.x_axis.cache_start
        idx2 = zarr_dataset.x_axis.to_idx(target_value=0.01)
        cache2 = zarr_dataset.x_axis.cache_start
        assert cache1 is not None
        assert cache2 is not None


# ============================================================================
# Test Binary Search
# ============================================================================


class TestBinarySearch:
    """Test binary search function."""

    @pytest.mark.parametrize(
        "data,target,expected",
        [
            ([1.0, 2.0, 3.0, 4.0, 5.0], 3.0, 3.0),  # Exact match (standard)
            ([5.0, 4.0, 3.0, 2.0, 1.0], 3.0, 3.0),  # Exact match (reverse)
        ],
    )
    def test_binary_search_exact_match(self, data, target, expected):
        """Test binary search with exact match."""
        standard = data[0] <= data[-1]
        idx = binary_search(target, lambda i: data[i], len(data), standard)
        assert data[idx] == expected

    def test_binary_search_approximate_standard(self):
        """Test binary search finding closest value (standard orientation)."""
        data = [1.0, 3.0, 5.0, 7.0, 9.0]
        idx = binary_search(4.0, lambda i: data[i], len(data), True)
        assert data[idx] in [3.0, 5.0]

    def test_binary_search_approximate_reverse(self):
        """Test binary search finding closest value (reverse orientation)."""
        data = [9.0, 7.0, 5.0, 3.0, 1.0]
        idx = binary_search(4.0, lambda i: data[i], len(data), False)
        assert data[idx] in [5.0, 3.0]

    @pytest.mark.parametrize(
        "target,expected_idx",
        [
            (0.5, 0),  # Before first
            (10.0, 4),  # After last
        ],
    )
    def test_binary_search_boundaries(self, target, expected_idx):
        """Test binary search at boundaries."""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        idx = binary_search(target, lambda i: data[i], len(data), True)
        assert idx == expected_idx
