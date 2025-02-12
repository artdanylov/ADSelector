# AD_Selector v0.1
<img src="screenshots/ads_1.png" width="1200" alt="Description">


## Maya 2024 Selector / Picker 


Main picker idea is to controls native maya selection sets with minimal and effective UI without creating any extra nodes in scenes. So all your selections always stored in scene file under ADSelectorData and can be used anytime without loading any extra data.

## Features

- **Minimalistic Design**: Clean and efficient user interface
- **Dockable UI**: Fully dockable window that integrates with Maya's interface
- **Smart Selection**:
  - Regular click: Select objects
  - Shift click: Add to current selection
  - Ctrl click: Remove from current selection
- **Btn Management**:
  - Export/Import to file
  - Quick export/import to move btns between Maya windows
  - Customize button colors
  - Reorder buttons

## Installation

Copy the `AD_Selector` folder to your Maya scripts directory
   ```
   C:\Users\UserName\Documents\maya\2024\scripts
   ```
   Note: Replace "UserName" with your Windows username
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
