# AD_Selector
<img src="screenshots/ads_1.png" width="1200" alt="Description">
Maya 2024 Selector / Picker script based on selection sets
- minimalistic design
- dockable UI
- export/import to file
- quick export/import to quickly move sets across maya windows
- recolor, change btns order, rename
- shift click adds to current selection, cntrl click removes from current selection


## Installation

Copy the `AD_Selector` folder to your Maya documents scripts directory

## Usage

Launch the tool in Maya using the following Python commands:

```python
import AD_Selector.ADSelector as ads
import importlib
importlib.reload(ads)
ads.initialize()
```

## Requirements

- Autodesk Maya 2024
