"""配置物件"""

import argparse
import os
import re

from wx import FileConfig

from .. import dialog


class Config:
    FILE_NAME_FORMAT_HINT = (
        '輸出檔案名稱格式支持替換:\n'
        '\n'
        '    %f : 原始PCB檔案名稱不含副檔名。\n'
        '    %p : PCB/專案標題來自PCB元數據。\n'
        '    %c : 公司名稱來自PCB元數據。\n'
        '    %r : 修訂版本來自PCB元數據。\n'
        '    %d : PCB日期來自元數據（如果有），'
        '否則為檔案修改日期。\n'
        '    %D : BOM生成日期。\n'
        '    %T : BOM生成時間。\n'
        '\n'
        '副檔名 .html 會自動添加。'
    )  # type: str

    # Helper constants
    bom_view_choices = ['僅BOM', '左右', '上下']
    layer_view_choices = ['F', 'FB', 'B']
    default_sort_order = [
        'C', 'R', 'L', 'D', 'U', 'Y', 'X', 'F', 'SW', 'A',
        '~',
        'HS', 'CNN', 'J', 'P', 'NT', 'MH',
    ]
    highlight_pin1_choices = ['無', '全部', '選中的']
    default_checkboxes = ['已採購', '已放置']
    html_config_fields = [
        'dark_mode', 'show_pads', 'show_fabrication', 'show_silkscreen',
        'highlight_pin1', 'redraw_on_drag', 'board_rotation', 'checkboxes',
        'bom_view', 'layer_view', 'offset_back_rotation',
        'kicad_text_formatting'
    ]
    default_show_group_fields = ["數值", "封裝"]

    # Defaults

    # HTML section
    dark_mode = False
    show_pads = True
    show_fabrication = False
    show_silkscreen = True
    redraw_on_drag = True
    highlight_pin1 = highlight_pin1_choices[0]
    board_rotation = 0
    offset_back_rotation = False
    checkboxes = ','.join(default_checkboxes)
    bom_view = bom_view_choices[1]
    layer_view = layer_view_choices[1]
    compression = True
    open_browser = True

    # General section
    bom_dest_dir = 'bom/'  # This is relative to pcb file directory
    bom_name_format = 'ibom'
    component_sort_order = default_sort_order
    component_blacklist = []
    blacklist_virtual = True
    blacklist_empty_val = False
    include_tracks = False
    include_nets = False
    kicad_text_formatting = True

    # Extra fields section
    extra_data_file = None
    netlist_initial_directory = ''  # This is relative to pcb file directory
    show_fields = default_show_group_fields
    group_fields = default_show_group_fields
    normalize_field_case = False
    board_variant_field = ''
    board_variant_whitelist = []
    board_variant_blacklist = []
    dnp_field = ''

    @staticmethod
    def _split(s):
        """Splits string by ',' and drops empty strings from resulting array"""
        return [a.replace('\\,', ',') for a in re.split(r'(?<!\\),', s) if a]

    @staticmethod
    def _join(lst):
        return ','.join([s.replace(',', '\\,') for s in lst])

    def __init__(self, version, local_dir):
        self.version = version
        self.local_config_file = os.path.join(local_dir, 'ibom.config.ini')
        self.global_config_file = os.path.join(
            os.path.dirname(__file__), '..', 'config.ini')

    def load_from_ini(self):
        """Init from config file if it exists."""
        if os.path.isfile(self.local_config_file):
            file = self.local_config_file
        elif os.path.isfile(self.global_config_file):
            file = self.global_config_file
        else:
            return

        f = FileConfig(localFilename=file)

        f.SetPath('/html_defaults')
        self.dark_mode = f.ReadBool('dark_mode', self.dark_mode)
        self.show_pads = f.ReadBool('show_pads', self.show_pads)
        self.show_fabrication = f.ReadBool(
            'show_fabrication', self.show_fabrication)
        self.show_silkscreen = f.ReadBool(
            'show_silkscreen', self.show_silkscreen)
        self.redraw_on_drag = f.ReadBool('redraw_on_drag', self.redraw_on_drag)
        self.highlight_pin1 = f.Read('highlight_pin1', self.highlight_pin1)
        self.board_rotation = f.ReadInt('board_rotation', self.board_rotation)
        self.offset_back_rotation = f.ReadBool(
            'offset_back_rotation', self.offset_back_rotation)
        self.checkboxes = f.Read('checkboxes', self.checkboxes)
        self.bom_view = f.Read('bom_view', self.bom_view)
        self.layer_view = f.Read('layer_view', self.layer_view)
        self.compression = f.ReadBool('compression', self.compression)
        self.open_browser = f.ReadBool('open_browser', self.open_browser)

        f.SetPath('/general')
        self.bom_dest_dir = f.Read('bom_dest_dir', self.bom_dest_dir)
        self.bom_name_format = f.Read('bom_name_format', self.bom_name_format)
        self.component_sort_order = self._split(f.Read(
            'component_sort_order',
            ','.join(self.component_sort_order)))
        self.component_blacklist = self._split(f.Read(
            'component_blacklist',
            ','.join(self.component_blacklist)))
        self.blacklist_virtual = f.ReadBool(
            'blacklist_virtual', self.blacklist_virtual)
        self.blacklist_empty_val = f.ReadBool(
            'blacklist_empty_val', self.blacklist_empty_val)
        self.include_tracks = f.ReadBool('include_tracks', self.include_tracks)
        self.include_nets = f.ReadBool('include_nets', self.include_nets)

        f.SetPath('/fields')
        self.show_fields = self._split(f.Read(
            'show_fields', self._join(self.show_fields)))
        self.group_fields = self._split(f.Read(
            'group_fields', self._join(self.group_fields)))
        self.normalize_field_case = f.ReadBool(
            'normalize_field_case', self.normalize_field_case)
        self.board_variant_field = f.Read(
            'board_variant_field', self.board_variant_field)
        self.board_variant_whitelist = self._split(f.Read(
            'board_variant_whitelist',
            self._join(self.board_variant_whitelist)))
        self.board_variant_blacklist = self._split(f.Read(
            'board_variant_blacklist',
            self._join(self.board_variant_blacklist)))
        self.dnp_field = f.Read('dnp_field', self.dnp_field)

        # migration from previous settings
        if self.highlight_pin1 == '0':
            self.highlight_pin1 = '無'
        if self.highlight_pin1 == '1':
            self.highlight_pin1 = '全部'

    def save(self, locally):
        file = self.local_config_file if locally else self.global_config_file
        print('儲存至', file)
        f = FileConfig(localFilename=file)

        f.SetPath('/html_defaults')
        f.WriteBool('dark_mode', self.dark_mode)
        f.WriteBool('show_pads', self.show_pads)
        f.WriteBool('show_fabrication', self.show_fabrication)
        f.WriteBool('show_silkscreen', self.show_silkscreen)
        f.WriteBool('redraw_on_drag', self.redraw_on_drag)
        f.Write('highlight_pin1', self.highlight_pin1)
        f.WriteInt('board_rotation', self.board_rotation)
        f.WriteBool('offset_back_rotation', self.offset_back_rotation)
        f.Write('checkboxes', self.checkboxes)
        f.Write('bom_view', self.bom_view)
        f.Write('layer_view', self.layer_view)
        f.WriteBool('compression', self.compression)
        f.WriteBool('open_browser', self.open_browser)

        f.SetPath('/general')
        bom_dest_dir = self.bom_dest_dir
        if bom_dest_dir.startswith(self.netlist_initial_directory):
            bom_dest_dir = os.path.relpath(
                bom_dest_dir, self.netlist_initial_directory)
        f.Write('bom_dest_dir', bom_dest_dir)
        f.Write('bom_name_format', self.bom_name_format)
        f.Write('component_sort_order',
                ','.join(self.component_sort_order))
        f.Write('component_blacklist',
                ','.join(self.component_blacklist))
        f.WriteBool('blacklist_virtual', self.blacklist_virtual)
        f.WriteBool('blacklist_empty_val', self.blacklist_empty_val)
        f.WriteBool('include_tracks', self.include_tracks)
        f.WriteBool('include_nets', self.include_nets)

        f.SetPath('/fields')
        f.Write('show_fields', self._join(self.show_fields))
        f.Write('group_fields', self._join(self.group_fields))
        f.WriteBool('normalize_field_case', self.normalize_field_case)
        f.Write('board_variant_field', self.board_variant_field)
        f.Write('board_variant_whitelist',
                self._join(self.board_variant_whitelist))
        f.Write('board_variant_blacklist',
                self._join(self.board_variant_blacklist))
        f.Write('dnp_field', self.dnp_field)
        f.Flush()

    def set_from_dialog(self, dlg):
        # type: (dialog.settings_dialog.SettingsDialogPanel) -> None
        # Html
        self.dark_mode = dlg.html.darkModeCheckbox.IsChecked()
        self.show_pads = dlg.html.showPadsCheckbox.IsChecked()
        self.show_fabrication = dlg.html.showFabricationCheckbox.IsChecked()
        self.show_silkscreen = dlg.html.showSilkscreenCheckbox.IsChecked()
        self.redraw_on_drag = dlg.html.continuousRedrawCheckbox.IsChecked()
        self.highlight_pin1 = self.highlight_pin1_choices[dlg.html.highlightPin1.Selection]
        self.board_rotation = dlg.html.boardRotationSlider.Value
        self.offset_back_rotation = \
            dlg.html.offsetBackRotationCheckbox.IsChecked()
        self.checkboxes = dlg.html.bomCheckboxesCtrl.Value
        self.bom_view = self.bom_view_choices[dlg.html.bomDefaultView.Selection]
        self.layer_view = self.layer_view_choices[
            dlg.html.layerDefaultView.Selection]
        self.compression = dlg.html.compressionCheckbox.IsChecked()
        self.open_browser = dlg.html.openBrowserCheckbox.IsChecked()

        # General
        self.bom_dest_dir = dlg.general.bomDirPicker.Path
        self.bom_name_format = dlg.general.fileNameFormatTextControl.Value
        self.component_sort_order = dlg.general.componentSortOrderBox.GetItems()
        self.component_blacklist = dlg.general.blacklistBox.GetItems()
        self.blacklist_virtual = \
            dlg.general.blacklistVirtualCheckbox.IsChecked()
        self.blacklist_empty_val = \
            dlg.general.blacklistEmptyValCheckbox.IsChecked()
        self.include_tracks = dlg.general.includeTracksCheckbox.IsChecked()
        self.include_nets = dlg.general.includeNetsCheckbox.IsChecked()

        # Fields
        self.extra_data_file = dlg.fields.extraDataFilePicker.Path
        self.show_fields = dlg.fields.GetShowFields()
        self.group_fields = dlg.fields.GetGroupFields()
        self.normalize_field_case = dlg.fields.normalizeCaseCheckbox.Value
        self.board_variant_field = dlg.fields.boardVariantFieldBox.Value
        if self.board_variant_field == dlg.fields.NONE_STRING:
            self.board_variant_field = ''
        self.board_variant_whitelist = list(
            dlg.fields.boardVariantWhitelist.GetCheckedStrings())
        self.board_variant_blacklist = list(
            dlg.fields.boardVariantBlacklist.GetCheckedStrings())
        self.dnp_field = dlg.fields.dnpFieldBox.Value
        if self.dnp_field == dlg.fields.NONE_STRING:
            self.dnp_field = ''

    def transfer_to_dialog(self, dlg):
        # type: (dialog.settings_dialog.SettingsDialogPanel) -> None
        # Html
        dlg.html.darkModeCheckbox.Value = self.dark_mode
        dlg.html.showPadsCheckbox.Value = self.show_pads
        dlg.html.showFabricationCheckbox.Value = self.show_fabrication
        dlg.html.showSilkscreenCheckbox.Value = self.show_silkscreen
        dlg.html.highlightPin1.Selection = 0
        if self.highlight_pin1 in self.highlight_pin1_choices:
            dlg.html.highlightPin1.Selection = \
                self.highlight_pin1_choices.index(self.highlight_pin1)
        dlg.html.continuousRedrawCheckbox.value = self.redraw_on_drag
        dlg.html.boardRotationSlider.Value = self.board_rotation
        dlg.html.offsetBackRotationCheckbox.Value = self.offset_back_rotation
        dlg.html.bomCheckboxesCtrl.Value = self.checkboxes
        dlg.html.bomDefaultView.Selection = self.bom_view_choices.index(
            self.bom_view)
        dlg.html.layerDefaultView.Selection = self.layer_view_choices.index(
            self.layer_view)
        dlg.html.compressionCheckbox.Value = self.compression
        dlg.html.openBrowserCheckbox.Value = self.open_browser

        # General
        import os.path
        if os.path.isabs(self.bom_dest_dir):
            dlg.general.bomDirPicker.Path = self.bom_dest_dir
        else:
            dlg.general.bomDirPicker.Path = os.path.join(
                self.netlist_initial_directory, self.bom_dest_dir)
        dlg.general.fileNameFormatTextControl.Value = self.bom_name_format
        dlg.general.componentSortOrderBox.SetItems(self.component_sort_order)
        dlg.general.blacklistBox.SetItems(self.component_blacklist)
        dlg.general.blacklistVirtualCheckbox.Value = self.blacklist_virtual
        dlg.general.blacklistEmptyValCheckbox.Value = self.blacklist_empty_val
        dlg.general.includeTracksCheckbox.Value = self.include_tracks
        dlg.general.includeNetsCheckbox.Value = self.include_nets

        # Fields
        dlg.fields.extraDataFilePicker.SetInitialDirectory(
            self.netlist_initial_directory)

        def safe_set_checked_strings(clb, strings):
            current = list(clb.GetStrings())
            if current:
                present_strings = [s for s in strings if s in current]
                not_present_strings = [s for s in current if s not in strings]
                clb.Clear()
                clb.InsertItems(present_strings + not_present_strings, 0)
                clb.SetCheckedStrings(present_strings)

        dlg.fields.SetCheckedFields(self.show_fields, self.group_fields)
        dlg.fields.normalizeCaseCheckbox.Value = self.normalize_field_case
        dlg.fields.boardVariantFieldBox.Value = self.board_variant_field
        dlg.fields.OnBoardVariantFieldChange(None)
        safe_set_checked_strings(dlg.fields.boardVariantWhitelist,
                                 self.board_variant_whitelist)
        safe_set_checked_strings(dlg.fields.boardVariantBlacklist,
                                 self.board_variant_blacklist)
        dlg.fields.dnpFieldBox.Value = self.dnp_field

        dlg.finish_init()

    @classmethod
    def add_options(cls, parser, version):
        # type: (argparse.ArgumentParser, str) -> None
        parser.add_argument('--show-dialog', action='store_true',
                            help='顯示配置對話框。所有其他標誌'
                                 '將被忽略。')
        parser.add_argument('--version', action='version', version=version)
        # Html
        parser.add_argument('--dark-mode', help='預設為暗模式。',
                            action='store_true')
        parser.add_argument('--hide-pads',
                            help='預設隱藏封裝的 pads。',
                            action='store_true')
        parser.add_argument('--show-fabrication',
                            help='預設顯示製造層。',
                            action='store_true')
        parser.add_argument('--hide-silkscreen',
                            help='預設隱藏絲印層。',
                            action='store_true')
        parser.add_argument('--highlight-pin1',
                            default=cls.highlight_pin1_choices[0],
                            const=cls.highlight_pin1_choices[1],
                            choices=cls.highlight_pin1_choices,
                            nargs='?',
                            help='突出顯示第一個引腳。')
        parser.add_argument('--no-redraw-on-drag',
                            help='預設不在拖動時重新繪製PCB。',
                            action='store_true')
        parser.add_argument('--board-rotation', type=int,
                            default=cls.board_rotation * 5,
                            help='板旋轉角度（-180 到 180）。 '
                                 '將四捨五入到5的倍數。')
        parser.add_argument('--offset-back-rotation',
                            help='將PCB背面偏移180度',
                            action='store_true')
        parser.add_argument('--checkboxes',
                            default=cls.checkboxes,
                            help='以逗號分隔的復選框列清單。')
        parser.add_argument('--bom-view', default=cls.bom_view,
                            choices=cls.bom_view_choices,
                            help='預設 BOM 視圖。')
        parser.add_argument('--layer-view', default=cls.layer_view,
                            choices=cls.layer_view_choices,
                            help='預設層視圖。')
        parser.add_argument('--no-compression',
                            help='禁用 PCB 數據壓縮。',
                            action='store_true')
        parser.add_argument('--no-browser', help='不啟動瀏覽器。',
                            action='store_true')

        # General
        parser.add_argument('--dest-dir', default=cls.bom_dest_dir,
                            help='BOM 檔案的目標目錄 '
                                 '相對於PCB檔案目錄。')
        parser.add_argument('--name-format', default=cls.bom_name_format,
                            help=cls.FILE_NAME_FORMAT_HINT.replace('%', '%%'))
        parser.add_argument('--include-tracks', action='store_true',
                            help='在輸出中包括軌跡/區域信息。 '
                                 '僅 F.Cu 和 B.Cu 層。')
        parser.add_argument('--include-nets', action='store_true',
                            help='在輸出中包括網表信息。')
        parser.add_argument('--sort-order',
                            help='元件的預設排序順序。 '
                                 '必須包含一次 "~"。',
                            default=','.join(cls.component_sort_order))
        parser.add_argument('--blacklist',
                            default=','.join(cls.component_blacklist),
                            help='列出用逗號分隔的黑名單元件 '
                                 '或帶有 * 的前綴。 '
                                 '例如 "X1,MH*"')
        parser.add_argument('--no-blacklist-virtual', action='store_true',
                            help='不要將虛擬元件列入黑名單。')
        parser.add_argument('--blacklist-empty-val', action='store_true',
                            help='將數值為空的元件列入黑名單。')

        # Fields section
        parser.add_argument('--netlist-file',
                            help='（已棄用）網表或XML檔案的路徑。')
        parser.add_argument('--extra-data-file',
                            help='網表或XML檔案的路徑。')
        parser.add_argument('--extra-fields',
                            help='傳遞 --extra-fields "X,Y" 是快捷方式 '
                                 '對 --show-fields 和 --group-fields '
                                 '使用 "Value,Footprint,X,Y" 值。')
        parser.add_argument('--show-fields',
                            default=cls._join(cls.show_fields),
                            help='BOM 中顯示的字段列表。')
        parser.add_argument('--group-fields',
                            default=cls._join(cls.group_fields),
                            help='元件將根據這些字段分組。')
        parser.add_argument('--normalize-field-case',
                            help='標準化額外字段名稱的大小寫。例如 "MPN" '
                                 '和 "mpn" 將被視為相同的字段。',
                            action='store_true')
        parser.add_argument('--variant-field',
                            help='存儲元件板變體的額外字段的名稱。')
        parser.add_argument('--variants-whitelist', default='',
                            help='包括在 BOM 中的板變體清單。使用 "<empty>" 表示 '
                                 '未設置或空值。')
        parser.add_argument('--variants-blacklist', default='',
                            help='排除在 BOM 中的板變體清單。使用 "<empty>" 表示 '
                                 '未設置或空值。')
        parser.add_argument('--dnp-field', default=cls.dnp_field,
                            help='表示不要填充狀態的額外字段名稱。具有 '
                                 '此字段不為空的元件將被排除。')

    def set_from_args(self, args):
        # type: (argparse.Namespace) -> None
        import math

        # Html
        self.dark_mode = args.dark_mode
        self.show_pads = not args.hide_pads
        self.show_fabrication = args.show_fabrication
        self.show_silkscreen = not args.hide_silkscreen
        self.highlight_pin1 = args.highlight_pin1
        self.redraw_on_drag = not args.no_redraw_on_drag
        self.board_rotation = math.fmod(args.board_rotation // 5, 37)
        self.offset_back_rotation = args.offset_back_rotation
        self.checkboxes = args.checkboxes
        self.bom_view = args.bom_view
        self.layer_view = args.layer_view
        self.compression = not args.no_compression
        self.open_browser = not args.no_browser

        # General
        self.bom_dest_dir = args.dest_dir
        self.bom_name_format = args.name_format
        self.component_sort_order = self._split(args.sort_order)
        self.component_blacklist = self._split(args.blacklist)
        self.blacklist_virtual = not args.no_blacklist_virtual
        self.blacklist_empty_val = args.blacklist_empty_val
        self.include_tracks = args.include_tracks
        self.include_nets = args.include_nets

        # Fields
        self.extra_data_file = args.extra_data_file or args.netlist_file
        if args.extra_fields is not None:
            self.show_fields = self.default_show_group_fields + \
                self._split(args.extra_fields)
            self.group_fields = self.show_fields
        else:
            self.show_fields = self._split(args.show_fields)
            self.group_fields = self._split(args.group_fields)
        self.normalize_field_case = args.normalize_field_case
        self.board_variant_field = args.variant_field
        self.board_variant_whitelist = self._split(args.variants_whitelist)
        self.board_variant_blacklist = self._split(args.variants_blacklist)
        self.dnp_field = args.dnp_field

    def get_html_config(self):
        import json
        d = {f: getattr(self, f) for f in self.html_config_fields}
        d["fields"] = self.show_fields
        return json.dumps(d)
