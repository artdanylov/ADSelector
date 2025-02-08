from cProfile import label
import os
from tabnanny import check
import maya.cmds as cmds
import maya.mel as mel
import json
from typing import Optional, Dict, List

def initialize():
    workspace = "ADSelector_WorkspaceControl"
    
    if cmds.workspaceControl(workspace, exists=True):
        cmds.deleteUI(workspace, control=True)
    
    showUI()

    cmds.workspaceControl(
        workspace,
        e=True,
        actLikeMayaUIElement=True,
    )

def ADSelectorUI(*args):
    global flowLayout
    MainSet()
    def selectorBtn(*args):
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning("No selection made.")
            return
        name = selection[0]
        name = name.replace(":","")
        name = uniqueName(name)
        btn = cmds.button(
                parent=flow,
                height=40,
                recomputeSize=1,
                label=name,
                command=lambda x, n=name: SelectAction(n),
            )
        PopupMenuBtn(btn)
        CreateSet(btn,selection)
    
    formMain = cmds.formLayout()
    addbtn = cmds.button(label="+", parent=formMain, command=selectorBtn)
    PopupMenuAddBtn(addbtn)
    
    flow = cmds.flowLayout(
        parent=formMain,
        columnSpacing=3,
        horizontal=1,
        wrap=1,
    )
    flowLayout = flow
    MainSetName,BtnOrderAttr = MainSet()
    BtnOderAttrString = cmds.getAttr(f'{MainSetName}.{BtnOrderAttr}')
    if BtnOderAttrString:
        BtnList = BtnOderAttrString.split(',')
        for Btn in BtnList:
            BtnName = name = Btn.split('_(')[0]
            BtnColor = Btn.split('_(')[1].split(')')[0]
            btn = cmds.button(
                    parent=flow,
                    height=40,
                    recomputeSize=1,
                    label=name,
                    backgroundColor=colorToValue(BtnColor),
                    command=lambda x, n=name: SelectAction(n),
                )
            PopupMenuBtn(btn)
    
    cmds.formLayout(formMain, edit=True,
        attachForm=[
            (addbtn, 'left', 0), (addbtn, 'top', 0), (addbtn, 'bottom', 0),
            (flow, 'left', 0), (flow, 'top', 0), (flow, 'right', 0), (flow, 'bottom', 0)
        ],
        attachControl=[
            (flow, 'left', 5, addbtn),
        ],
        attachPosition=[
            (addbtn, 'left', 10, 0)
        ],
    )

def showUI():
   deleteControl("ADSelector_WorkspaceControl")
   workspace = cmds.workspaceControl(
       "ADSelector_WorkspaceControl",
        retain=True,
        floating=False,
        #minimumWidth=True,
        actLikeMayaUIElement=True,
        loadImmediately=False,
        uiScript="import AD_Selector.ADSelector as ads; ads.ADSelectorUI()"
    )    
   return workspace
   
def refreshUI():
    existing_buttons = cmds.layout(flowLayout, q=True, childArray=True) or []
    for btn in existing_buttons:
        try:
            cmds.button(btn, edit=True, visible=False)
            cmds.deleteUI(btn)
        except:
            continue
    MainSetName, BtnOrderAttr = MainSet()
    BtnOrderAttrString = cmds.getAttr(f'{MainSetName}.{BtnOrderAttr}')
    if BtnOrderAttrString:
        BtnList = BtnOrderAttrString.split(',')
        for Btn in BtnList:
            if not Btn:
                continue
            try:
                BtnName = name = Btn.split('_(')[0]
                BtnColor = Btn.split('_(')[1].split(')')[0]
                btn = cmds.button(
                    parent=flowLayout,
                    height=40,
                    recomputeSize=1,
                    label=name,
                    backgroundColor=colorToValue(BtnColor),
                    command=lambda x, n=name: SelectAction(n),
                )
                PopupMenuBtn(btn)
            except:
                continue



#ReOrderUI Start
def move_item(scroll_list, direction):
    selected = cmds.textScrollList(scroll_list, query=True, selectItem=True)
    if not selected:
        return

    current_items = cmds.textScrollList(scroll_list, query=True, allItems=True)
    if not current_items:
        return
       
    current_index = current_items.index(selected[0])
    new_index = current_index + direction

    if 0 <= new_index < len(current_items):
        current_items[current_index], current_items[new_index] = current_items[new_index], current_items[current_index]

        cmds.textScrollList(scroll_list, edit=True, removeAll=True)
        cmds.textScrollList(scroll_list, edit=True, append=current_items)
        cmds.textScrollList(scroll_list, edit=True, selectItem=selected[0])

def load_default_order(scroll_list, *args):
    MainSetName, BtnOrderAttr = MainSet()
    if cmds.objExists(MainSetName):
        current_order = cmds.getAttr(f"{MainSetName}.{BtnOrderAttr}")
        if current_order:
            list_items = [item.strip() for item in current_order.split(',') if item.strip()]
            cmds.textScrollList(scroll_list, edit=True, removeAll=True)
            cmds.textScrollList(scroll_list, edit=True, append=list_items)

def apply_changes(scroll_list, *args):
    MainSetName, BtnOrderAttr = MainSet()
    BtnOderAttrString = cmds.getAttr(f'{MainSetName}.{BtnOrderAttr}')
    current_items = cmds.textScrollList(scroll_list, query=True, allItems=True)
    if current_items:
        result_string = ','.join(current_items)
        cmds.setAttr(f"{MainSetName}.{BtnOrderAttr}", result_string, type="string")
    refreshUI()


def ReOrder_UI():
    window_name = "ADSReOrderUI"

    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    window = cmds.window(
        window_name,
        title="ReOrder Buttons",
        width=100,
        height=100
    )

    main_form = cmds.formLayout()

    scroll_list = cmds.textScrollList(
        allowMultiSelection=False,
        height=100,
        width=100
    )

    up_btn = cmds.iconTextButton(
        style='iconOnly',
        image='moveUVUp.png',
        width=20,
        height=20,
        command=lambda *args: move_item(scroll_list, -1)
    )

    down_btn = cmds.iconTextButton(
        style='iconOnly',
        image='moveUVDown.png',
        width=20,
        height=20,
        command=lambda *args: move_item(scroll_list, 1)
    )

    load_btn = cmds.button(
        label="Load Default Order",
        height=30,
        command=lambda x: load_default_order(scroll_list)
    )

    apply_btn = cmds.button(
        label="Apply Changes",
        height=30,
        backgroundColor=[0.2, 0.8, 0.2],
        command=lambda x: apply_changes(scroll_list)
    )
    cmds.formLayout(main_form, edit=True, 
        attachForm=[
            (scroll_list, 'left', 5),
            (scroll_list, 'top', 5),
            (up_btn, 'top', 5),
            (up_btn, 'right', 5),
            (down_btn, 'right', 5),
            (load_btn, 'left', 5),
            (load_btn, 'right', 5),
            (apply_btn, 'left', 5),
            (apply_btn, 'right', 5),
            (apply_btn, 'bottom', 5)
        ],
        attachControl=[
            (scroll_list, 'bottom', 5, load_btn),
            (down_btn, 'top', 5, up_btn),
            (load_btn, 'bottom', 5, apply_btn)
        ],
        attachPosition=[
            (scroll_list, 'right', 5, 90),
            (up_btn, 'left', 0, 90),
            (down_btn, 'left', 0, 90)
        ]
    )
    cmds.showWindow(window)
    load_default_order(scroll_list)
#ReOrderUI End

#JSon Data Process Start
def PathToTempFile():
    MainSetName,BtnOrderAttr = MainSet() 
    script_path = cmds.internalVar(userScriptDir=True)
    temp_dir = os.path.join(script_path, "AD_Selector", "Temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    temp_file = os.path.join(temp_dir, f"{MainSetName}_temp.json")
    return temp_file
    
def DeleteAllSets():
    MainSetName,BtnOrderAttr = MainSet()
    members = cmds.sets(MainSetName, q=1)
    cmds.delete(members)
    refreshUI()

def ExportJson(btn, QuickExportAll="True", SaveAs="False" ):
    if QuickExportAll=="True":
        ExportMode='All'
        EndMsg='Quick Exported: All Btns'
    if QuickExportAll=="False":
        ExportMode=BtnName(btn)
        EndMsg='Quick Exported: ' + BtnName(btn)
    
    if SaveAs=="True":
        json_path = cmds.fileDialog2(
            fileFilter="JSON Files (*.json)",
            dialogStyle=2,
            fileMode=0,
            caption="Save Selector Data",
            okCaption="Save",
        )
        json_path=json_path[0]
        EndMsg='Saved to: ' + json_path
    else:
        json_path = PathToTempFile()    
    MainSetName,BtnOrderAttr = MainSet()    
    currentOrder = ""
    if cmds.attributeQuery(BtnOrderAttr, node=MainSetName, exists=True):
        currentOrder = cmds.getAttr(f'{MainSetName}.{BtnOrderAttr}') or ""
        
    data = {
        "ExportMode": ExportMode,
        "mainSet": {"name": MainSetName,"order": currentOrder},
        "childSets": {}
        }
    childs = cmds.sets(MainSetName, q=1) or []
    for child in childs:
        if cmds.objExists(child):
            members = cmds.sets(child, q=1) or []
            if members:
                data["childSets"][child] = {"selection": members}
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(EndMsg)
    
def LoadJson(LoadAs="False"):
    if LoadAs=='True':
        json_path = cmds.fileDialog2(
            fileFilter="JSON Files (*.json)",
            dialogStyle=2,
            fileMode=1,
            caption="Load Selector Data",
            okCaption="Load",
        )
        json_path=json_path[0]
    else:
        json_path = PathToTempFile()  

    with open(json_path, 'r') as f:
        data = json.load(f)
    
    Import = data["ExportMode"]
    MainSet()
    MainSetName,BtnOrderAttr = MainSet()
    if LoadAs=='True'or Import == "All":
        CurrentSets=cmds.sets(MainSetName, q=1)
        cmds.delete(CurrentSets)
        MainSet()
        newOrder = data["mainSet"].get("order", "")
        cmds.setAttr(f'{MainSetName}.{BtnOrderAttr}', newOrder, type='string')        
        for child, child_data in data["childSets"].items():
            if not cmds.objExists(child):
                cmds.sets(name=child, empty=True)
            members = child_data.get("selection", [])
            existing_members = [m for m in members if cmds.objExists(m)]
            if existing_members:
                cmds.sets(existing_members, add=child)
                cmds.sets(child, add=MainSetName)
        if LoadAs=='True':
            print('Loaded from: ', json_path)
        else:
            print('Quick Imported All')
    
    if Import != "All":
        newOrder = data["mainSet"].get("order", "")
        newOrderList = newOrder.split(',') if ',' in newOrder else [newOrder]
        ImportSel = data["childSets"].get('ADS_'+Import).get("selection",[])
        currentOrder = cmds.getAttr(f'{MainSetName}.{BtnOrderAttr}')
        if currentOrder:
            OrderList = currentOrder.split(',') if ',' in currentOrder else [currentOrder]
    
        for newOrder in newOrderList:
            if Import in newOrder:
                ImportOrder=newOrder
                if currentOrder:
                    if ImportOrder in OrderList:
                        ImportOrder=newOrder.replace(Import,Import+"NEW")
                    
        members=cmds.sets(MainSetName,q=1)
        if members:
            for member in members:
                if Import in member:
                    ImportMember=member.replace(Import,Import+"NEW")
        if not members:
            ImportMember="ADS_" + Import

        if currentOrder:
            newOrder=currentOrder+","+ImportOrder
        if not currentOrder:
            newOrder=ImportOrder

        #print(ImportOrder, ImportMember, newOrder), 
        cmds.setAttr(f'{MainSetName}.{BtnOrderAttr}', newOrder , type='string')  
        cmds.sets(name=ImportMember, empty=True)
        cmds.sets(ImportSel, add=ImportMember)
        cmds.sets(ImportMember, add=MainSetName)
        print('Added BTN: ', Import)
    refreshUI()
#JSon Data Process End

def get_colors():
    return {
        'Default': (0.363, 0.363, 0.363),
        'Pink': (0.996, 0.776, 0.776),
        'Blue': (0.678, 0.847, 0.902),
        'Green': (0.776, 0.937, 0.808),
        'Lavender': (0.859, 0.788, 0.937),
        'Peach': (1.000, 0.855, 0.725),
        'LightBlue': (0.804, 0.871, 0.996),
        'Yellow': (1.000, 0.957, 0.702),
        'Coral': (0.941, 0.722, 0.725),
        'Seafoam': (0.725, 0.941, 0.871),
        'Purple': (0.914, 0.808, 0.922)
    }
    
def colorToValue(colorName):
    colors = get_colors()
    return colors.get(colorName, colors['Default'])

def valueToColor(colorValue):
    colors = get_colors()
    colorValue = tuple(round(x, 3) for x in colorValue)
    for name, value in colors.items():
        if tuple(round(x, 3) for x in value) == colorValue:
            return name
    return 'Default'

def SetBtnColor(btn, color_value):
    cmds.button(btn, edit=True, backgroundColor=color_value)
    MainSetName,BtnOrderAttr = MainSet()
    currentOrder = cmds.getAttr(f'{MainSetName}.{BtnOrderAttr}')
    if not currentOrder: return
    OrderList = currentOrder.split(',') if ',' in currentOrder else [currentOrder]
    if len(OrderList) == 1:
        if BtnName(btn) in OrderList[0]:
            old_color = OrderList[0].split('_(')[1].split(')')[0]
            new_color = valueToColor(color_value)
            OrderList[0] = OrderList[0].replace(old_color, new_color)
            newOrder = ','.join(OrderList)
            cmds.setAttr(f'{MainSetName}.{BtnOrderAttr}', newOrder, type='string')
            return   
    for i, element in enumerate(OrderList):
        if BtnName(btn) in element:
            old_color = element.split('_(')[1].split(')')[0]
            new_color = valueToColor(color_value)
            OrderList[i] = element.replace(old_color, new_color)
    newOrder = ','.join(OrderList)
    cmds.setAttr(f'{MainSetName}.{BtnOrderAttr}', newOrder, type='string')

def MainSet():
    MainSetName = "ADSelectorData"
    BtnOrderAttr = 'BtnOrder'
    if not cmds.objExists(MainSetName):
        MainSet=cmds.sets(name=MainSetName, empty=True)
        cmds.addAttr(MainSet, longName=BtnOrderAttr, dataType='string')
    return MainSetName, BtnOrderAttr

def BtnName(btn):
    BtnName = cmds.button(btn, query=True, label=True)
    return BtnName
def BtnToSetName(btn):
    return f"ADS_{BtnName(btn)}"
def SetNameToBtn(setName):
    return setName.split('ADS_')[1]

def uniqueName(name):
    existing_buttons = cmds.layout(flowLayout, q=True, childArray=True) or []
    for btn in existing_buttons:
        ExistName=cmds.button(btn, q=1, label=1)
        if name == ExistName:
            name=name + "NEW"
    return name

def CreateSet(btn, selection):
    MainSetName,BtnOrderAttr = MainSet()
    btnSet = cmds.sets(name=BtnToSetName(btn), empty=True)
    cmds.sets(selection, add=btnSet)
    cmds.sets(btnSet, add=MainSetName)
    
    currentOrder = cmds.getAttr(f'{MainSetName}.{BtnOrderAttr}') or ""
    newOrder = currentOrder + ("," if currentOrder else "") + BtnName(btn) + "_(Default)"
    cmds.setAttr(f'{MainSetName}.{BtnOrderAttr}', newOrder, type='string')   

def Rename(btn):
    result = cmds.promptDialog(
        title='Rename',
        message='Enter new name:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel',
        text=cmds.button(btn, query=True, label=True)
        )
   
    if result == 'OK':
        old_name = BtnName(btn)
        new_name = cmds.promptDialog(query=True, text=True)
        cmds.button(btn, edit=True, label=new_name, command=lambda x, n=new_name: SelectAction(n))
        cmds.rename('ADS_' + old_name, 'ADS_' + new_name)

        MainSetName,BtnOrderAttr = MainSet()
        currentOrder = cmds.getAttr(f'{MainSetName}.{BtnOrderAttr}')
        if not currentOrder: return
        OrderList = currentOrder.split(',') if ',' in currentOrder else [currentOrder]
        if len(OrderList) == 1:
            if old_name in OrderList[0]:
                old_name = OrderList[0].split('_(')[0]
                OrderList[0] = OrderList[0].replace(old_name, new_name)
                newOrder = ','.join(OrderList)
                cmds.setAttr(f'{MainSetName}.{BtnOrderAttr}', newOrder, type='string')
                refreshUI()
                return   
        for i, element in enumerate(OrderList):
            if old_name in element:
                old_name = element.split('_(')[0]
                OrderList[i] = element.replace(old_name, new_name)
        newOrder = ','.join(OrderList)
        cmds.setAttr(f'{MainSetName}.{BtnOrderAttr}', newOrder, type='string')
        refreshUI()
        return
    return None    

def AddFromSelection(btn):
    selection=cmds.ls(selection=1)
    cmds.sets(selection, add=BtnToSetName(btn))
def RemoveFromSelection(btn):
    selection=cmds.ls(selection=1)
    cmds.sets(selection, remove=BtnToSetName(btn))
    
def PopupMenuBtn(btn):
    colors = get_colors()
    popup = cmds.popupMenu(parent=btn, button=3)

    cmds.menuItem(
        label="Quick Export",
        parent=popup,
        command=lambda x, b=btn:ExportJson(b,QuickExportAll='False')
    )
    cmds.menuItem(divider=True, parent=popup)        
    color_menu = cmds.menuItem(label="Change Color", subMenu=True, parent=popup)
    for color_name, color_value in colors.items():
        cmds.menuItem(
            label=color_name,
            parent=color_menu,
            command=lambda x, b=btn, c=color_value: SetBtnColor(b, c)
        )   
    cmds.menuItem(divider=True, parent=popup)
    cmds.menuItem(
        label="Add Selection",
        parent=popup,
        command=lambda x, b=btn:AddFromSelection(b)
    )
    cmds.menuItem(
        label="Remove Selection",
        parent=popup,
        command=lambda x, b=btn:RemoveFromSelection(b)
    )
    cmds.menuItem(divider=True, parent=popup)
    cmds.menuItem(
        label="Rename",
        parent=popup,
        command=lambda x, b=btn: Rename(b)
    )
    cmds.menuItem(divider=True, parent=popup)
    cmds.menuItem(
        label="Delete",
        parent=popup,
        command=lambda x, b=btn: deleteAction(b)
    )


def PopupMenuAddBtn(addbtn):
    popup = cmds.popupMenu(parent=addbtn, button=3)     
    cmds.menuItem(divider=True, parent=popup)
    cmds.menuItem(
        label="Quick Import",
        parent=popup,
        command=lambda *args: LoadJson(LoadAs="False")
    )
    cmds.menuItem(
        label="Quick Export All",
        parent=popup,
        command=lambda *args: ExportJson(btn=None,QuickExportAll='True',SaveAs='False')
    )
    cmds.menuItem(divider=True, parent=popup)
    cmds.menuItem(
        label="Load from file",
        parent=popup,
        command=lambda x: LoadJson(LoadAs="True")
    )
    cmds.menuItem(
        label="Save to file",
        parent=popup,
        command=lambda x: ExportJson(btn=None,QuickExportAll='True',SaveAs='True')
    )


    cmds.menuItem(divider=True, parent=popup)
    cmds.menuItem(
        label="ReOrder",
        parent=popup,
        command=lambda x: ReOrder_UI()
    )
    cmds.menuItem(divider=True, parent=popup)
    cmds.menuItem(
        label="Delete All",
        parent=popup,
        command=lambda x: DeleteAllSets()
    )    
    
def SelectAction(name,*args):
    mods = cmds.getModifiers()
    ctrl_pressed = (mods & 4) > 0
    shift_pressed = (mods & 1) > 0

    if ctrl_pressed:
        #print('ctrlClick')
        current_selection = cmds.ls(selection=True) or []
        btn_selection = cmds.ls('ADS_'+ name)
        cmds.select(btn_selection, deselect=True)
        
    elif shift_pressed:
        #print('shiftClick')
        current_selection = cmds.ls(selection=True) or []
        btn_selection = cmds.ls('ADS_'+ name)
        cmds.select(btn_selection, add=True)
        
    else:
        #print('Click')
        cmds.select(clear=1)
        cmds.select(cmds.ls('ADS_'+ name))
            
    
def deleteAction(btn):
    cmds.button(btn,e=1,visible=0)
    cmds.delete(BtnToSetName(btn)) 
    MainSetName,BtnOrderAttr = MainSet()
    currentOrder = cmds.getAttr(f'{MainSetName}.{BtnOrderAttr}')
    if not currentOrder: return
    OrderList = currentOrder.split(',') if ',' in currentOrder else [currentOrder]
    if len(OrderList) == 1:
        if BtnName(btn) in OrderList[0]:
            cmds.setAttr(f'{MainSetName}.{BtnOrderAttr}', '', type='string')
        return    
    for i, element in enumerate(OrderList):
        if BtnName(btn) in element:
            BtnToRemove = element + ','
            OrderList[i] = element.replace(BtnToRemove,'')     
    newOrder = ','.join(OrderList)
    cmds.setAttr(f'{MainSetName}.{BtnOrderAttr}', newOrder, type='string')     

def deleteControl(control):
    if cmds.workspaceControl(control, q=True, exists=True):
        cmds.workspaceControl(control,e=True, close=True)
        cmds.deleteUI(control,control=True)

    


if __name__ == "__main__":
   initialize()
