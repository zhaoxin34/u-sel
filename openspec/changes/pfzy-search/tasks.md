## 1. Setup

- [x] 1.1 Add `pfzy` dependency to `pyproject.toml`
- [x] 1.2 Run `uv sync` to install new dependency

## 2. Core Implementation

- [x] 2.1 Implement `fuzzy_search()` function with fzy scoring and indices return
- [x] 2.2 Implement `build_highlighted_markup()` function for Textual markup generation
- [x] 2.3 Update `ItemWidget` class to accept and render match indices

## 3. Search Integration

- [x] 3.1 Replace `_do_search()` substring matching with pfzy fuzzy matching
- [x] 3.2 Integrate fuzzy search with multi-field scoring (title, output, group)
- [x] 3.3 Preserve numeric quick select logic (digit detection)
- [x] 3.4 Update `_render_results()` to pass indices to ItemWidget

## 4. UI Enhancement

- [x] 4.1 Define CSS class for matched character highlighting
- [x] 4.2 Test highlight rendering in Textual

## 5. Testing

- [x] 5.1 Add test cases for fuzzy matching (nfp → new float pane)
- [x] 5.2 Add test cases for highlight markup generation
- [x] 5.3 Add test cases for numeric selection preservation
- [x] 5.4 Run full test suite to verify no regressions

## 6. Verification

- [x] 6.1 Manual testing: type "nfp" to match "new float pane"
- [x] 6.2 Verify match highlighting is visible
- [x] 6.3 Verify group filtering works correctly
- [x] 6.4 Verify existing placeholder functionality ({{g|...}}, {{i:...}}) still works
