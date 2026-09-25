from calibre.utils.config import JSONConfig
from qt.core import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .log import get_log_text


PREFS = JSONConfig('plugins/crosspoint_reader')
PREFS.defaults['host'] = '192.168.4.1'
PREFS.defaults['port'] = 81
PREFS.defaults['path'] = '/'
PREFS.defaults['chunk_size'] = 2048
PREFS.defaults['debug'] = False
PREFS.defaults['fetch_metadata'] = False
PREFS.defaults['send_to_root'] = False
PREFS.defaults['overwrite_existing'] = False
PREFS.defaults['upload_template'] = ''
PREFS.defaults['upload_retries'] = 3
PREFS.defaults['retry_delay'] = 2
PREFS.defaults['book_cooldown'] = 1
PREFS.defaults['socket_timeout'] = 30
# Optimizer settings (mirrors the CrossPoint web server optimizer).
PREFS.defaults['optimize'] = False
PREFS.defaults['optimize_grayscale'] = True
PREFS.defaults['optimize_auto_crop'] = False
PREFS.defaults['optimize_quality'] = 85
PREFS.defaults['optimize_split'] = True
PREFS.defaults['device_target'] = 'auto'  # 'auto' | 'X4' | 'X3'
# Image geometry + grayscale tuning (fork additions).
PREFS.defaults['optimize_enlarge'] = True
PREFS.defaults['optimize_rotate_landscape'] = False   # opt-in: rotates wide figures sideways
PREFS.defaults['optimize_fill_mode'] = 'fit'          # 'fit' | 'fill'
PREFS.defaults['optimize_grayscale_mode'] = 'lightness'  # 'luma' | 'lightness'
PREFS.defaults['optimize_brighten'] = 0               # extra gamma lift, 0..100


class CrossPointConfigWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.host = QLineEdit(self)
        self.port = QSpinBox(self)
        self.port.setRange(1, 65535)
        self.path = QLineEdit(self)
        self.upload_template = QLineEdit(self)
        self.chunk_size = QSpinBox(self)
        self.chunk_size.setRange(512, 65536)
        self.upload_retries = QSpinBox(self)
        self.upload_retries.setRange(0, 10)
        self.retry_delay = QSpinBox(self)
        self.retry_delay.setRange(0, 60)
        self.retry_delay.setSuffix(' s')
        self.book_cooldown = QSpinBox(self)
        self.book_cooldown.setRange(0, 60)
        self.book_cooldown.setSuffix(' s')
        self.socket_timeout = QSpinBox(self)
        self.socket_timeout.setRange(5, 300)
        self.socket_timeout.setSuffix(' s')
        self.debug = QCheckBox('Enable debug logging', self)
        self.fetch_metadata = QCheckBox('Fetch metadata for side-loaded books (downloads each once on connect)', self)
        self.send_to_root = QCheckBox('Send to root (ignore any template)', self)
        self.overwrite_existing = QCheckBox('Overwrite file if it already exists on the device', self)

        # Optimizer controls.
        self.optimize = QCheckBox('Optimize EPUBs before transfer', self)
        self.optimize_grayscale = QCheckBox('Convert images to grayscale', self)
        self.optimize_auto_crop = QCheckBox('Auto-crop uniform margins', self)
        self.optimize_split = QCheckBox(
            'Split large chapters/paragraphs, remove fonts (prevents out-of-memory)', self)
        self.optimize_quality = QSpinBox(self)
        self.optimize_quality.setRange(1, 100)
        self.optimize_quality.setSuffix('%')
        self.device_target = QComboBox(self)
        self.device_target.addItem('Auto-detect', 'auto')
        self.device_target.addItem('X4 (480×800)', 'X4')
        self.device_target.addItem('X3 (528×792)', 'X3')
        self.optimize_enlarge = QCheckBox('Enlarge block figures to fill the page (inline glyphs left as-is)', self)
        self.optimize_rotate_landscape = QCheckBox('Rotate wide figures sideways to fill the page (off = keep upright)', self)
        self.optimize_fill_mode = QComboBox(self)
        self.optimize_fill_mode.addItem('Fit (whole image, may letterbox)', 'fit')
        self.optimize_fill_mode.addItem('Fill (cover screen, centre-crop overflow)', 'fill')
        self.optimize_grayscale_mode = QComboBox(self)
        self.optimize_grayscale_mode.addItem('Lightness (brighter — best for colour covers)', 'lightness')
        self.optimize_grayscale_mode.addItem('Luminance (ITU-R 601 — matches web UI)', 'luma')
        self.optimize_brighten = QSpinBox(self)
        self.optimize_brighten.setRange(0, 100)
        self.optimize_brighten.setSuffix('%')

        self.host.setText(PREFS['host'])
        self.port.setValue(PREFS['port'])
        self.path.setText(PREFS['path'])
        self.upload_template.setText(PREFS['upload_template'])
        self.upload_template.setPlaceholderText("Leave blank to use Calibre's send-to-device template")
        self.chunk_size.setValue(PREFS['chunk_size'])
        self.upload_retries.setValue(PREFS['upload_retries'])
        self.retry_delay.setValue(PREFS['retry_delay'])
        self.book_cooldown.setValue(PREFS['book_cooldown'])
        self.socket_timeout.setValue(PREFS['socket_timeout'])
        self.debug.setChecked(PREFS['debug'])
        self.fetch_metadata.setChecked(PREFS['fetch_metadata'])
        self.send_to_root.setChecked(PREFS['send_to_root'])
        self.overwrite_existing.setChecked(PREFS['overwrite_existing'])
        self.optimize.setChecked(PREFS['optimize'])
        self.optimize_grayscale.setChecked(PREFS['optimize_grayscale'])
        self.optimize_auto_crop.setChecked(PREFS['optimize_auto_crop'])
        self.optimize_split.setChecked(PREFS['optimize_split'])
        self.optimize_quality.setValue(PREFS['optimize_quality'])
        idx = self.device_target.findData(PREFS['device_target'])
        self.device_target.setCurrentIndex(idx if idx >= 0 else 0)
        self.optimize_enlarge.setChecked(PREFS['optimize_enlarge'])
        self.optimize_rotate_landscape.setChecked(PREFS['optimize_rotate_landscape'])
        idx_fill = self.optimize_fill_mode.findData(PREFS['optimize_fill_mode'])
        self.optimize_fill_mode.setCurrentIndex(idx_fill if idx_fill >= 0 else 0)
        idx_gs = self.optimize_grayscale_mode.findData(PREFS['optimize_grayscale_mode'])
        self.optimize_grayscale_mode.setCurrentIndex(idx_gs if idx_gs >= 0 else 0)
        self.optimize_brighten.setValue(PREFS['optimize_brighten'])

        layout.addRow('Host', self.host)
        layout.addRow('Port', self.port)

        notice = QLabel('Host and port settings are fallback values used only when the device is not auto-discoverable by UDP broadcast.')
        notice.setWordWrap(True)
        notice.setStyleSheet('color: gray; font-style: italic;')
        layout.addRow('', notice)

        layout.addRow('Upload path', self.path)
        layout.addRow('Upload template', self.upload_template)
        layout.addRow('Chunk size', self.chunk_size)

        reliability_heading = QLabel('<b>Upload reliability</b>')
        layout.addRow(reliability_heading)
        reliability_notice = QLabel('Retries resend the current book from the beginning after transient WebSocket failures.')
        reliability_notice.setWordWrap(True)
        reliability_notice.setStyleSheet('color: gray; font-style: italic;')
        layout.addRow('', reliability_notice)
        layout.addRow('Upload retries', self.upload_retries)
        layout.addRow('Retry delay', self.retry_delay)
        layout.addRow('Delay between books', self.book_cooldown)
        layout.addRow('Socket timeout', self.socket_timeout)

        layout.addRow('', self.debug)
        layout.addRow('', self.fetch_metadata)
        layout.addRow('', self.send_to_root)
        layout.addRow('', self.overwrite_existing)

        sep = QFrame(self)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addRow(sep)

        opt_heading = QLabel('<b>Optimizer</b>')
        layout.addRow(opt_heading)
        opt_notice = QLabel('Resizes images to the screen (enlarging and rotating landscape '
                            'images to fill it), converts to grayscale and re-encodes as JPEG, '
                            'then rewrites the EPUB. A summary is shown after each transfer.')
        opt_notice.setWordWrap(True)
        opt_notice.setStyleSheet('color: gray; font-style: italic;')
        layout.addRow('', opt_notice)
        layout.addRow('', self.optimize)
        layout.addRow('Device target', self.device_target)
        layout.addRow('JPEG quality', self.optimize_quality)
        layout.addRow('', self.optimize_grayscale)
        layout.addRow('Grayscale method', self.optimize_grayscale_mode)
        layout.addRow('Lighten', self.optimize_brighten)
        layout.addRow('', self.optimize_auto_crop)
        layout.addRow('', self.optimize_enlarge)
        layout.addRow('', self.optimize_rotate_landscape)
        layout.addRow('Fill mode', self.optimize_fill_mode)
        layout.addRow('', self.optimize_split)

        self.optimize.toggled.connect(self._sync_optimizer_enabled)
        self._sync_optimizer_enabled(self.optimize.isChecked())

        self.log_view = QPlainTextEdit(self)
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText('Discovery log will appear here when debug is enabled.')
        self._refresh_logs()

        refresh_btn = QPushButton('Refresh Log', self)
        refresh_btn.clicked.connect(self._refresh_logs)
        log_layout = QHBoxLayout()
        log_layout.addWidget(refresh_btn)

        layout.addRow('Log', self.log_view)
        layout.addRow('', log_layout)

    def save(self):
        PREFS['host'] = self.host.text().strip() or PREFS.defaults['host']
        PREFS['port'] = int(self.port.value())
        PREFS['path'] = self.path.text().strip() or PREFS.defaults['path']
        PREFS['upload_template'] = self.upload_template.text().strip()
        PREFS['chunk_size'] = int(self.chunk_size.value())
        PREFS['upload_retries'] = int(self.upload_retries.value())
        PREFS['retry_delay'] = int(self.retry_delay.value())
        PREFS['book_cooldown'] = int(self.book_cooldown.value())
        PREFS['socket_timeout'] = int(self.socket_timeout.value())
        PREFS['debug'] = bool(self.debug.isChecked())
        PREFS['fetch_metadata'] = bool(self.fetch_metadata.isChecked())
        PREFS['send_to_root'] = bool(self.send_to_root.isChecked())
        PREFS['overwrite_existing'] = bool(self.overwrite_existing.isChecked())
        PREFS['optimize'] = bool(self.optimize.isChecked())
        PREFS['optimize_grayscale'] = bool(self.optimize_grayscale.isChecked())
        PREFS['optimize_auto_crop'] = bool(self.optimize_auto_crop.isChecked())
        PREFS['optimize_split'] = bool(self.optimize_split.isChecked())
        PREFS['optimize_quality'] = int(self.optimize_quality.value())
        PREFS['device_target'] = self.device_target.currentData()
        PREFS['optimize_enlarge'] = bool(self.optimize_enlarge.isChecked())
        PREFS['optimize_rotate_landscape'] = bool(self.optimize_rotate_landscape.isChecked())
        PREFS['optimize_fill_mode'] = self.optimize_fill_mode.currentData()
        PREFS['optimize_grayscale_mode'] = self.optimize_grayscale_mode.currentData()
        PREFS['optimize_brighten'] = int(self.optimize_brighten.value())

    def _sync_optimizer_enabled(self, enabled):
        for w in (self.optimize_grayscale, self.optimize_auto_crop,
                  self.optimize_split, self.optimize_quality, self.device_target,
                  self.optimize_enlarge, self.optimize_rotate_landscape,
                  self.optimize_fill_mode, self.optimize_grayscale_mode,
                  self.optimize_brighten):
            w.setEnabled(enabled)

    def _refresh_logs(self):
        self.log_view.setPlainText(get_log_text())

    def validate(self):
        return True


class CrossPointConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('CrossPoint Reader')
        self.widget = CrossPointConfigWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(self.widget)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
