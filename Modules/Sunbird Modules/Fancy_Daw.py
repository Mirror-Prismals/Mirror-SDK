# fancy_paperdaw.py
import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QHBoxLayout, QLabel, QFrame,
    QGraphicsItem, QMessageBox, QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox, QSpinBox, QColorDialog, QListWidget, QListWidgetItem, QMenu,
    QFileDialog
)
from PyQt5.QtCore import QRectF, Qt, QTimer, QEvent, QPointF
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPen, QCursor, QTransform
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtMultimedia import QMediaContent  # Add this import
from PyQt5.QtGui import QMovie
# ------------------ Model Definitions ------------------
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel
class TextClip:
    """Represents a text clip with properties."""
    def __init__(self, text, start_time, duration, track, clip_id, color="#87CEEB"):
        self.text = text
        self.start_time = start_time  # in seconds
        self.duration = duration      # in seconds
        self.track = track
        self.id = clip_id
        self.color = color            # Hex color code

    def to_dict(self):
        """Serialize the TextClip to a dictionary."""
        return {
            'text': self.text,
            'start_time': self.start_time,
            'duration': self.duration,
            'track': self.track,
            'id': self.id,
            'color': self.color
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize a TextClip from a dictionary."""
        return cls(
            text=data['text'],
            start_time=data['start_time'],
            duration=data['duration'],
            track=data['track'],
            clip_id=data['id'],
            color=data.get('color', "#87CEEB")
        )


class Layer:
    """Represents a layer containing lanes and clips."""
    def __init__(self, name, color="#8080FF"):  # Default color
        self.name = name
        self.lanes = []
        self.clips = []
        self.visible = True
        self.color = color  # New color attribute

    def to_dict(self):
        return {
            'name': self.name,
            'lanes': [lane['name'] for lane in self.lanes],
            'clips': [clip.to_dict() for clip in self.clips],
            'visible': self.visible,
            'color': self.color  # Serialize color
        }

    @classmethod
    def from_dict(cls, data):
        layer = cls(name=data['name'], color=data.get('color', "#8080FF"))
        layer.lanes = [{'name': lane_name}] 
        for lane_data in data.get('lanes', []):
            lane_name = lane_data.get('name', 'Unnamed Lane')  # Ensure 'name' is extracted properly
 # Ensure 'name' is extracted properly

        layer.visible = data.get('visible', True)
        for clip_data in data.get('clips', []):
            clip = TextClip.from_dict(clip_data)
            layer.clips.append(clip)
        return layer


class Project:
    """Manages all layers and clips in the project."""
    def __init__(self):
        self.layers = []
        self.next_id = 1

    def add_layer(self, name):
        layer = Layer(name)
        self.layers.append(layer)
        return layer

    def remove_layer(self, layer):
        self.layers.remove(layer)

    def add_clip(self, text, start_time, duration, track, layer, color="#150f18"):
        clip = TextClip(text, start_time, duration, track, self.next_id, color)
        layer.clips.append(clip)
        self.next_id += 1
        return clip

    def remove_clip(self, clip, layer):
        layer.clips = [c for c in layer.clips if c.id != clip.id]

    def to_dict(self):
        return {
            'layers': [layer.to_dict() for layer in self.layers]
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize a Project from a dictionary."""
        project = cls()
        for layer_data in data.get('layers', []):
            layer = Layer.from_dict(layer_data)
            project.layers.append(layer)
            # Update next_id to avoid ID conflicts
            max_clip_id = max((clip.id for clip in layer.clips), default=0)
            project.next_id = max(project.next_id, max_clip_id + 1)
        return project


class Layer:
    """Represents a layer containing lanes and clips."""
    def __init__(self, name, color="#8080FF"):  # Default color
        self.name = name
        self.lanes = []
        self.clips = []
        self.visible = True
        self.color = color  # New color attribute

    def to_dict(self):
        return {
            'name': self.name,
            'lanes': [lane['name'] for lane in self.lanes],
            'clips': [clip.to_dict() for clip in self.clips],
            'visible': self.visible,
            'color': self.color
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize a Layer from a dictionary."""
        layer = cls(name=data.get('name', 'Unnamed Layer'), color=data.get('color', "#8080FF"))
        
        # Handle lanes as a list of strings
        for lane_name in data.get('lanes', []):
            layer.lanes.append({'name': lane_name})

        layer.visible = data.get('visible', True)
        for clip_data in data.get('clips', []):
            clip = TextClip.from_dict(clip_data)
            layer.clips.append(clip)
        return layer


# ------------------ Custom Graphics Item ------------------

class DraggableClip(QGraphicsRectItem):
    """A draggable, editable, and color-customizable text clip in the timeline."""
    def __init__(self, clip: TextClip, scale_factor_x=100, scale_factor_y=100, main_window=None):
        super().__init__()
        self.clip = clip
        self.scale_factor_x = scale_factor_x  # pixels per second (horizontal)
        self.scale_factor_y = scale_factor_y  # pixels per lane (vertical)
        self.main_window = main_window      # Reference to main window

        # Initial Rectangle
        self.setRect(
            0,  # Position will be handled by setPos
            0,
            self.clip.duration * self.scale_factor_x,
            self.scale_factor_y * 1  # Slightly smaller to fit within lane
        )
        self.setBrush(QBrush(QColor(self.clip.color)))
        self.setPen(QPen(QColor("#150f18"), 2))
        self.setFlags(
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemIsMovable
        )
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.OpenHandCursor)

        # Add Text
        self.text_item = QGraphicsTextItem(self.clip.text, self)
        self.text_item.setDefaultTextColor(QColor("#839496"))
        self.text_item.setFont(QFont("Times New Roman", 12))
        self.text_item.setPos(10, 10)

        # Position the clip
        self.update_position()

    def mousePressEvent(self, event):
        """Change cursor on press."""
        self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Update clip properties on release."""
        new_pos = self.pos()
        self.clip.start_time = new_pos.x() / self.scale_factor_x
        self.clip.track = int(new_pos.y() / self.scale_factor_y)
        self.snap_to_grid()
        self.update_position()
        super().mouseReleaseEvent(event)
        if self.main_window:
            self.main_window.update_clip_properties(self.clip)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to edit clip text and duration."""
        self.main_window.edit_clip_properties(self.clip)
        super().mouseDoubleClickEvent(event)

    def hoverEnterEvent(self, event):
        """Change cursor on hover."""
        self.setCursor(Qt.OpenHandCursor)
        super().hoverEnterEvent(event)

    def hoverMoveEvent(self, event):
        """Display tooltip with clip properties."""
        tooltip = (
            f"Text: {self.clip.text}\n"
            f"Start: {self.clip.start_time:.2f}s\n"
            f"Duration: {self.clip.duration:.2f}s\n"
            f"Track: {self.clip.track}\n"
            f"Color: {self.clip.color}"
        )
        self.setToolTip(tooltip)
        super().hoverMoveEvent(event)

    def update_position(self):
        """Ensure the visual position matches the clip's properties."""
        self.setPos(self.clip.start_time * self.scale_factor_x, self.clip.track * self.scale_factor_y)
        self.setBrush(QBrush(QColor(self.clip.color)))
        # Adjust text size based on scaling
        current_font = self.text_item.font()
        current_font.setPointSize(int(12 * (self.scale_factor_x / 100)))
        self.text_item.setFont(current_font)

    def snap_to_grid(self):
        """Snap clip to the nearest 16th note based on tempo."""
        if self.main_window:
            interval = self.main_window.sixteenth_note_duration
            snapped_start = round(self.clip.start_time / interval) * interval
            self.clip.start_time = snapped_start
            # Update clip position
            self.setPos(self.clip.start_time * self.scale_factor_x, self.clip.track * self.scale_factor_y)

    def contextMenuEvent(self, event):
        """Context menu for editing and deleting the clip."""
        menu = QMenu()
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        action = menu.exec_(QCursor.pos())
        if action == edit_action:
            self.main_window.edit_clip_properties(self.clip)
        elif action == delete_action:
            self.main_window.delete_clip(self.clip)
        super().contextMenuEvent(event)


# ------------------ View Definitions ------------------

class FancyToolbar(QWidget):
    """Customized toolbar with styled buttons."""
    def __init__(self, add_clip_callback, add_lane_callback, add_layer_callback,
                 settings_callback, save_callback, load_callback):
        super().__init__()
        self.init_ui(add_clip_callback, add_lane_callback, add_layer_callback,
                     settings_callback, save_callback, load_callback)

    def init_ui(self, add_clip_callback, add_lane_callback, add_layer_callback,
               settings_callback, save_callback, load_callback):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(20)

        # Application Title
        title = QLabel("Mirror")
        title.setFont(QFont("Times New Roman", 18))
        title.setStyleSheet("color: #a0a0a0;")  # Ruby Red Color
        layout.addWidget(title)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().Expanding, spacer.sizePolicy().Preferred)
        layout.addWidget(spacer)

        # Add Clip Button
        add_clip_btn = QPushButton("Add Clip")
        add_clip_btn.setIcon(QIcon.fromTheme("list-add"))
        add_clip_btn.setStyleSheet("""
            QPushButton {
                background-color: #150f18;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #150f18;
            }
        """)
        add_clip_btn.clicked.connect(add_clip_callback)
        layout.addWidget(add_clip_btn)

        # Add Lane Button
        add_lane_btn = QPushButton("Add Lane")
        add_lane_btn.setIcon(QIcon.fromTheme("list-add"))
        add_lane_btn.setStyleSheet("""
            QPushButton {
                background-color: #150f18;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #150f18;
            }
        """)
        add_lane_btn.clicked.connect(add_lane_callback)
        layout.addWidget(add_lane_btn)

        # Add Layer Button
        add_layer_btn = QPushButton("Add Layer")
        add_layer_btn.setIcon(QIcon.fromTheme("folder-new"))
        add_layer_btn.setStyleSheet("""
            QPushButton {
                background-color: #150f18;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #150f18;
            }
        """)
        add_layer_btn.clicked.connect(add_layer_callback)
        layout.addWidget(add_layer_btn)

        # Save Session Button
        save_btn = QPushButton("Save")
        save_btn.setIcon(QIcon.fromTheme("document-save"))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #150f18;
                color: #2E3440;
                border: none;
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #150f18;
            }
        """)
        save_btn.clicked.connect(save_callback)
        layout.addWidget(save_btn)

        # Load Session Button
        load_btn = QPushButton("Load")
        load_btn.setIcon(QIcon.fromTheme("document-open"))
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #150f18;
                color: #2E3440;
                border: none;
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #150f18;
            }
        """)
        load_btn.clicked.connect(load_callback)
        layout.addWidget(load_btn)

        # Settings Button
        settings_btn = QPushButton("Settings")
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #150f18;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #150f18;
            }
        """)
        settings_btn.clicked.connect(settings_callback)
        layout.addWidget(settings_btn)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #150f18;")  # Dark background to contrast with ruby colors


class FancyPaperdawView(QMainWindow):
    """Main window with enhanced features."""
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Daw")
        self.showFullScreen()  # Launch in maximized window
        self.setWindowIcon(QIcon.fromTheme("document-edit"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Add Fancy Toolbar with Save and Load callbacks
        self.toolbar = FancyToolbar(
            self.add_clip_dialog,
            self.add_lane,
            self.add_layer_dialog,
            self.open_settings,
            self.save_session,
            self.load_session
        )
        self.main_layout.addWidget(self.toolbar)

        # Timeline and Controls Layout
        self.timeline_layout = QHBoxLayout()
        self.main_layout.addLayout(self.timeline_layout)

        # Graphics View for Timeline
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("""
            background-color: #FFFFFF;
            border: 2px solid #150f18;
            border-radius: 15px;
        """)
        self.timeline_layout.addWidget(self.view, stretch=8)

        # Control Panel
        self.control_panel = QFrame()
        self.control_panel.setFixedWidth(300)
        self.control_panel.setStyleSheet("""
            background-color: #EAF0E7;
            border: 2px solid #150f18;
            border-radius: 15px;
        """)
        self.timeline_layout.addWidget(self.control_panel, stretch=2)

        control_layout = QVBoxLayout()
        control_layout.setContentsMargins(20, 20, 20, 20)
        control_layout.setSpacing(20)

        # Layer Management Section
        layer_label = QLabel("Layers")
        layer_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        layer_label.setStyleSheet("color: #404080;")  # Ruby Red Color
        control_layout.addWidget(layer_label)

        # Layer List
        self.layer_list = QListWidget()
        self.layer_list.setSelectionMode(QListWidget.SingleSelection)
        self.layer_list.itemClicked.connect(self.change_active_layer)
        self.layer_list.setStyleSheet("""
            QListWidget {
                background-color: #150f18;
                color: #ECEFF4;
                border: 1px solid #8080FF;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #202040;
                color: #8080FF;
            }
        """)
        control_layout.addWidget(self.layer_list)

        # Layer Buttons
        layer_btn_layout = QHBoxLayout()
        add_layer_btn = QPushButton("+Layer")
        add_layer_btn.setToolTip("Add Layer")
        add_layer_btn.setStyleSheet("""
            QPushButton {
                background-color: #150f18;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #150f18;
            }
        """)
        add_layer_btn.clicked.connect(self.add_layer_dialog)
        delete_layer_btn = QPushButton("-Layer")
        delete_layer_btn.setToolTip("Delete Layer")
        delete_layer_btn.setStyleSheet("""
            QPushButton {
                background-color: #150f18;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #150f18;
            }
        """)
        delete_layer_btn.clicked.connect(self.delete_layer)
        layer_btn_layout.addWidget(add_layer_btn)
        layer_btn_layout.addWidget(delete_layer_btn)
        control_layout.addLayout(layer_btn_layout)

        # Playback Controls Label
        playback_label = QLabel("Playback Controls")
        playback_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        playback_label.setStyleSheet("color: #000000;")  # Ruby Red Color
        control_layout.addWidget(playback_label)

        # Instructions for Playback Controls
        playback_instructions = QLabel("Press 'P' to Play\nPress 'Spacebar' to Stop")
        playback_instructions.setFont(QFont("Times New Roman", 12))
        playback_instructions.setStyleSheet("color: #000000;")
        playback_instructions.setAlignment(Qt.AlignLeft)
        control_layout.addWidget(playback_instructions)

        # Tempo Control
        tempo_label = QLabel("Tempo (BPM)")
        tempo_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        tempo_label.setStyleSheet("color: #000000;")  # Ruby Red Color
        control_layout.addWidget(tempo_label)

        self.tempo_input = QSpinBox()
        self.tempo_input.setRange(30, 300)
        self.tempo_input.setValue(120)
        self.tempo_input.setSuffix(" BPM")
        self.tempo_input.setStyleSheet("""
            QSpinBox {
                background-color: #150f18;
                color: #ECEFF4;
                border: 1px solid #008080;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.tempo_input.valueChanged.connect(self.update_tempo)
        control_layout.addWidget(self.tempo_input)

        # Clip Properties Display
        properties_label = QLabel("Clip Properties")
        properties_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        properties_label.setStyleSheet("color: #000000;")  # Ruby Red Color
        control_layout.addWidget(properties_label)

        self.properties_display = QLabel("Select a clip to see properties.")
        self.properties_display.setWordWrap(True)
        self.properties_display.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background-color: #8080FF;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        control_layout.addWidget(self.properties_display)

        # Spacer
        control_layout.addStretch()

        self.control_panel.setLayout(control_layout)

        # Status Bar
        self.status = self.statusBar()
        self.status.setStyleSheet("background-color: #ffffff; color: #444444;")
        self.status.showMessage("Ready")

        # Set Overall Style
        self.setStyleSheet("""
            QMainWindow {
                background-color: 008080;
            }
            QLabel {
                color: #eeffee;
            }
        """)

        # Playback Timer
        self.playback_timer = QTimer()
        self.playback_timer.setInterval(100)  # Update every 100 ms
        self.playback_timer.timeout.connect(self.update_playback)
        self.current_play_time = 0  # in seconds

        # Tempo and Timeline Settings
        self.tempo = self.tempo_input.value()  # BPM
        self.sixteenth_note_duration = 60 / (self.tempo * 4)  # Duration of a 16th note in seconds

        # Flags
        self.is_playing = False

        # Initialize Layers
        self.active_layer = None
        self.initialize_layers()

        # Timeline at the Bottom
        self.timeline_height = 50  # Height in pixels
        self.timeline = QGraphicsRectItem(0, 0, 100000, self.timeline_height)
        self.timeline.setBrush(QBrush(QColor("#434C5E")))
        self.timeline.setPen(QPen(QColor("#BF616A"), 2))
        self.timeline.setZValue(1)  # Ensure timeline is above other items
        self.scene.addItem(self.timeline)

        # Initialize scale factors before adding lanes to prevent AttributeError
        self.scale_factor_x = 100  # pixels per second (horizontal)
        self.scale_factor_y = 100  # pixels per lane (vertical)

        # Draw initial timeline
        self.draw_timeline()

        # Enable Scrolling for Infinite Lanes
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # Keyboard Shortcuts
        self.view.setFocusPolicy(Qt.StrongFocus)
        self.view.keyPressEvent = self.handle_key_press

    # ------------------ Layer Management Methods ------------------

    def initialize_layers(self):
        """Initialize with a default layer."""
        default_layer = self.model.add_layer("Program:")
        self.active_layer = default_layer
        self.update_layer_list()
        #self.add_lane_visual(default_layer, "Lane 1")  # Add an initial lane to the default layer

    def add_layer_dialog(self):
        """Open dialog to add a new layer."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Layer")
        dialog.setFixedSize(300, 150)
        layout = QFormLayout(dialog)

        name_input = QLineEdit()
        layout.addRow("Layer Name:", name_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text()
            if name:
                new_layer = self.model.add_layer(name)
                self.active_layer = new_layer
                self.update_layer_list()
                self.add_lane_visual(new_layer, "Lane 1")  # Add an initial lane to the new layer
            else:
                QMessageBox.warning(self, "Input Error", "Layer name cannot be empty.")

    def delete_layer(self):
        """Delete the selected layer."""
        selected_items = self.layer_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a layer to delete.")
            return
        selected_item = selected_items[0]
        layer = selected_item.data(Qt.UserRole)
        if len(self.model.layers) == 1:
            QMessageBox.warning(self, "Deletion Error", "Cannot delete the last remaining layer.")
            return
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete '{layer.name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Remove graphical items of the layer
            for lane in layer.lanes:
                self.scene.removeItem(lane['rect'])
                self.scene.removeItem(lane['label'])
            for clip in layer.clips:
                for item in self.scene.items():
                    if isinstance(item, DraggableClip) and item.clip.id == clip.id:
                        self.scene.removeItem(item)
                        break
            # Remove layer from model
            self.model.remove_layer(layer)
            # Update layer list and set active layer
            self.update_layer_list()
            if self.model.layers:
                self.active_layer = self.model.layers[-1]
            else:
                self.active_layer = None
            self.properties_display.setText("Select a clip to see properties.")
            self.draw_timeline()

    def update_layer_list(self):
        """Update the layer list in the control panel."""
        self.layer_list.blockSignals(True)  # Prevent triggering signals while updating
        self.layer_list.clear()
        for layer in self.model.layers:
            item = QListWidgetItem(layer.name)
            item.setCheckState(Qt.Checked if layer.visible else Qt.Unchecked)
            item.setData(Qt.UserRole, layer)
            self.layer_list.addItem(item)
        if self.active_layer in self.model.layers:
            self.layer_list.setCurrentRow(self.model.layers.index(self.active_layer))
        self.layer_list.blockSignals(False)
        self.layer_list.itemChanged.connect(self.toggle_layer_visibility)

    def toggle_layer_visibility(self, item: QListWidgetItem):
        """Toggle visibility of a layer."""
        layer = item.data(Qt.UserRole)
        layer.visible = (item.checkState() == Qt.Checked)
        # Show or hide lanes and clips of the layer
        for lane in layer.lanes:
            lane['rect'].setVisible(layer.visible)
            lane['label'].setVisible(layer.visible)
        for clip in layer.clips:
            for item in self.scene.items():
                if isinstance(item, DraggableClip) and item.clip.id == clip.id:
                    item.setVisible(layer.visible)
                    break

    def change_active_layer(self, item: QListWidgetItem):
        """Change the active layer based on selection."""
        layer = item.data(Qt.UserRole)
        self.active_layer = layer
        # Update the background color of QGraphicsView
        self.view.setStyleSheet(f"""
            background-color: {layer.color};
            border: 2px solid #150f18;
            border-radius: 15px;
        """)


    # ------------------ Playback Control Methods ------------------

    def play(self):
        """Start playback."""
        if not self.is_playing:
            self.is_playing = True
            self.playback_timer.start()
            self.status.showMessage("Playing")

    def pause(self):
        """Pause playback."""
        if self.is_playing:
            self.is_playing = False
            self.playback_timer.stop()
            self.status.showMessage("Paused")

    def stop(self):
        """Stop playback."""
        if self.is_playing:
            self.is_playing = False
            self.playback_timer.stop()
        self.current_play_time = 0
        # Reset view to the beginning
        self.view.horizontalScrollBar().setValue(0)
        self.status.showMessage("Stopped")

    def update_playback(self):
        """Simulate playback by scrolling the view."""
        self.current_play_time += 0.1  # Increment by 0.1 seconds
        x_position = self.current_play_time * self.scale_factor_x
        self.view.horizontalScrollBar().setValue(int(x_position))

        # Check for end of timeline (e.g., max clip end time)
        max_end_time = max(
            (clip.start_time + clip.duration)
            for layer in self.model.layers
            for clip in layer.clips
        ) if any(layer.clips for layer in self.model.layers) else 100
        if self.current_play_time > max_end_time:
            self.stop()

    # ------------------ Clip Management Methods ------------------

    def add_clip_dialog(self):
        """Open dialog to add a new clip."""
        if self.active_layer is None:
            QMessageBox.warning(self, "No Active Layer", "Please add and select a layer before adding clips.")
            return

        if not self.active_layer.lanes:
            QMessageBox.warning(self, "No Lanes", "Please add a lane to the active layer before adding clips.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Text Clip")
        dialog.setFixedSize(400, 300)
        layout = QFormLayout(dialog)

        text_input = QLineEdit()
        start_time_input = QSpinBox()
        start_time_input.setRange(0, 100000)  # Increased range for infinite lanes
        start_time_input.setSuffix(" s")
        duration_input = QSpinBox()
        duration_input.setRange(1, 100000)
        duration_input.setSuffix(" s")
        track_input = QSpinBox()
        track_input.setRange(0, len(self.active_layer.lanes) - 1 if self.active_layer.lanes else 0)

        color_btn = QPushButton("Select Color")
        color_display = QLabel()
        color_display.setFixedSize(40, 20)
        color_display.setStyleSheet(f"background-color: #FFFFFF; border: 1px solid #FFFFFF;")
        selected_color = "#FFFFFF"  # Default ruby red color

        def choose_color():
            nonlocal selected_color
            color = QColorDialog.getColor()
            if color.isValid():
                selected_color = color.name()
                color_display.setStyleSheet(f"background-color: {selected_color}; border: 1px solid #BF616A;")

        color_btn.clicked.connect(choose_color)

        color_layout = QHBoxLayout()
        color_layout.addWidget(color_btn)
        color_layout.addWidget(color_display)

        layout.addRow("Text:", text_input)
        layout.addRow("Start Time (s):", start_time_input)
        layout.addRow("Duration (s):", duration_input)
        layout.addRow("Track:", track_input)
        layout.addRow("Color:", color_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            text = text_input.text()
            start_time = start_time_input.value()
            duration = duration_input.value()
            track = track_input.value()
            color = selected_color
            if text:
                self.add_clip(text, start_time, duration, track, color)
            else:
                QMessageBox.warning(self, "Input Error", "Text cannot be empty.")

    def add_clip(self, text, start_time, duration, track, color="#FFFFFF"):
        """Add a new clip to the scene and model."""
        clip = self.model.add_clip(text, start_time, duration, track, self.active_layer, color)
        self.add_graphics_clip(clip)
        self.draw_timeline()  # Redraw timeline if necessary

    def add_graphics_clip(self, clip: TextClip):
        """Create and add a draggable clip to the scene."""
        graphics_clip = DraggableClip(clip, self.scale_factor_x, self.scale_factor_y, self)
        self.scene.addItem(graphics_clip)

    def edit_clip_properties(self, clip: TextClip):
        """Open dialog to edit clip's text and duration."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Clip")
        dialog.setFixedSize(400, 300)
        layout = QFormLayout(dialog)

        text_input = QLineEdit(clip.text)
        duration_input = QSpinBox()
        duration_input.setRange(1, 100000)
        duration_input.setSuffix(" s")
        duration_input.setValue(int(clip.duration))

        color_btn = QPushButton("Select Color")
        color_display = QLabel()
        color_display.setFixedSize(40, 20)
        color_display.setStyleSheet(f"background-color: {clip.color}; border: 1px solid #BF616A;")
        selected_color = clip.color

        def choose_color():
            nonlocal selected_color
            color = QColorDialog.getColor()
            if color.isValid():
                selected_color = color.name()
                color_display.setStyleSheet(f"background-color: {selected_color}; border: 1px solid #BF616A;")

        color_btn.clicked.connect(choose_color)

        color_layout = QHBoxLayout()
        color_layout.addWidget(color_btn)
        color_layout.addWidget(color_display)

        layout.addRow("Text:", text_input)
        layout.addRow("Duration (s):", duration_input)
        layout.addRow("Color:", color_layout)

        # Delete Button
        delete_btn = QPushButton("Delete Clip")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #BF616A;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #D8DEE9;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_clip(clip))

        buttons_layout = QHBoxLayout()
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        buttons_layout.addWidget(buttons)
        buttons_layout.addWidget(delete_btn)
        layout.addRow(buttons_layout)

        if dialog.exec_() == QDialog.Accepted:
            new_text = text_input.text()
            new_duration = duration_input.value()
            new_color = selected_color
            if new_text:
                clip.text = new_text
                clip.duration = new_duration
                clip.color = new_color
                self.update_clip_visual(clip)
                self.update_clip_properties(clip)
                self.draw_timeline()  # Redraw timeline if necessary
            else:
                QMessageBox.warning(self, "Input Error", "Text cannot be empty.")

    def delete_clip(self, clip: TextClip):
        """Delete the specified clip."""
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                    f"Are you sure you want to delete the clip '{clip.text}'?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Remove graphical item
            for item in self.scene.items():
                if isinstance(item, DraggableClip) and item.clip.id == clip.id:
                    self.scene.removeItem(item)  # Ensure you're removing from the correct scene
                    break
            # Remove from model
            self.model.remove_clip(clip, self.active_layer)
            self.properties_display.setText("Select a clip to see properties.")
            self.draw_timeline()  # Redraw timeline if necessary

    def add_graphics_clip(self, clip: TextClip):
        """Create and add a draggable clip to the scene."""
        graphics_clip = DraggableClip(clip, self.scale_factor_x, self.scale_factor_y, self)
        self.scene.addItem(graphics_clip)

    def update_clip_visual(self, clip: TextClip):
        """Update the visual representation of a clip."""
        for item in self.scene.items():
            if isinstance(item, DraggableClip) and item.clip.id == clip.id:
                item.text_item.setPlainText(clip.text)
                item.setBrush(QBrush(QColor(clip.color)))
                break

    def update_clip_properties(self, clip: TextClip):
        """Display properties of the selected clip."""
        properties = (
            f"Text: {clip.text}\n"
            f"Start Time: {clip.start_time:.2f} s\n"
            f"Duration: {clip.duration:.2f} s\n"
            f"Track: {clip.track}\n"
            f"Color: {clip.color}"
        )
        self.properties_display.setText(properties)

    # ------------------ Lane Management Methods ------------------

    def add_lane(self):
        """Add a new lane to the active layer."""
        if self.active_layer is None:
            QMessageBox.warning(self, "No Active Layer", "Please add and select a layer before adding lanes.")
            return
        lane_number = len(self.active_layer.lanes) + 1
        lane_name = f"Lane {lane_number}"
        self.add_lane_visual(self.active_layer, lane_name)
        self.draw_timeline()

    def add_lane_visual(self, layer: Layer, lane_name: str):
        lane_height = 100
        lane_number = len(layer.lanes) + 1
        lane_width = 100000  # Extremely large to simulate infinity
        rect = QGraphicsRectItem(0, (lane_number - 1) * lane_height, lane_width, lane_height)
        rect.setBrush(QBrush(QColor("#FFFFFF")))  # Default color for lanes
        rect.setPen(QPen(QColor("#e0e0e0"), 2))  # Ruby Red Border
        rect.setZValue(-1)  # Ensure lanes are beneath clips but above timeline
        rect.setVisible(layer.visible)
        self.scene.addItem(rect)

        # Add lane label
        label = QGraphicsTextItem(lane_name)
        label.setDefaultTextColor(QColor("#ffffff"))  # White text for lanes
        label.setFont(QFont("Times New Roman", 12, QFont.Bold))
        label.setPos(10, (lane_number - 1) * lane_height + (lane_height - label.boundingRect().height()) / 2)
        label.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        label.setVisible(layer.visible)
        self.scene.addItem(label)

        # Store lane information in the model with 'rect' and 'label'
        layer.lanes.append({'rect': rect, 'label': label, 'name': lane_name})

        # Connect double-click event for color picking
        def pick_lane_color(event):
            color = QColorDialog.getColor()  # Open color picker
            if color.isValid():
                selected_color = color.name()  # Get the selected color hex code
                rect.setBrush(QBrush(QColor(selected_color)))  # Apply the selected color to the lane's background

        # Set double-click to trigger the color picker
        label.mouseDoubleClickEvent = pick_lane_color
        label.setCursor(Qt.PointingHandCursor)


    def edit_lane_properties_factory(self, lane_label, layer: Layer, lane_number: int):
        """Factory to create a double-click event handler for lane labels."""
        def edit_lane_properties(event):
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Lane")
            dialog.setFixedSize(300, 200)
            layout = QFormLayout(dialog)

            # Lane Name Input
            name_input = QLineEdit(lane_label.toPlainText())
            layout.addRow("Lane Name:", name_input)

            # Color Picker Button and Display
            color_btn = QPushButton("Select Color")
            color_display = QLabel()
            color_display.setFixedSize(40, 20)
            # Initialize with current lane color or default if not set
            current_color = layer.lanes[lane_number - 1].get('color', "#8080FF")
            color_display.setStyleSheet(f"background-color: {current_color}; border: 1px solid #BF616A;")
            selected_color = current_color

            def choose_color():
                nonlocal selected_color
                color = QColorDialog.getColor(QColor(selected_color), self, "Choose Lane Color")
                if color.isValid():
                    selected_color = color.name()
                    color_display.setStyleSheet(f"background-color: {selected_color}; border: 1px solid #BF616A;")

            color_btn.clicked.connect(choose_color)

            color_layout = QHBoxLayout()
            color_layout.addWidget(color_btn)
            color_layout.addWidget(color_display)
            layout.addRow("Color:", color_layout)

            # Delete Lane Button
            delete_btn = QPushButton("Delete Lane")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #BF616A;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #D8DEE9;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_lane(layer, lane_label))
            layout.addRow(delete_btn)

            # OK and Cancel Buttons
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec_() == QDialog.Accepted:
                new_name = name_input.text().strip()
                if new_name:
                    lane_label.setPlainText(new_name)
                    # Update lane color if it has changed
                    if selected_color != layer.lanes[lane_number - 1].get('color', "#8080FF"):
                        layer.lanes[lane_number - 1]['color'] = selected_color
                        layer.lanes[lane_number - 1]['rect'].setBrush(QBrush(QColor(selected_color)))
                else:
                    QMessageBox.warning(self, "Input Error", "Lane name cannot be empty.")

        return edit_lane_properties


    def delete_lane(self, layer: Layer, lane_label: QGraphicsTextItem):
        """Delete the specified lane."""
        lane_index = None
        for idx, lane in enumerate(layer.lanes):
            if lane['label'] == lane_label:
                lane_index = idx
                break
        if lane_index is not None:
            reply = QMessageBox.question(self, 'Confirm Deletion',
                                         f"Are you sure you want to delete '{lane_label.toPlainText()}'?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                # Remove graphical items
                self.scene.removeItem(layer.lanes[lane_index]['rect'])
                self.scene.removeItem(layer.lanes[lane_index]['label'])
                # Remove clips in this lane
                clips_to_remove = [clip for clip in layer.clips if clip.track == lane_index]
                for clip in clips_to_remove:
                    self.delete_clip(clip)
                # Remove lane from model
                layer.lanes.pop(lane_index)
                # Update lane numbers and labels
                for idx in range(lane_index, len(layer.lanes)):
                    lane = layer.lanes[idx]
                    lane['rect'].setY(idx * self.scale_factor_y)
                    lane['label'].setPos(10, idx * self.scale_factor_y + (self.scale_factor_y - lane['label'].boundingRect().height()) / 2)
                    lane['label'].setPlainText(f"Lane {idx + 1}")
                    # Update clip track numbers
                    for clip in layer.clips:
                        if clip.track > lane_index:
                            clip.track -= 1
                            # Update clip position
                            for item in self.scene.items():
                                if isinstance(item, DraggableClip) and item.clip.id == clip.id:
                                    item.setPos(clip.start_time * self.scale_factor_x, clip.track * self.scale_factor_y)
                                    break
                self.draw_timeline()

    # ------------------ Timeline Management Methods ------------------

    def draw_timeline(self):
        """Draw or update the timeline at the bottom."""
        # Remove existing timeline
        self.scene.removeItem(self.timeline)

        # Create new timeline
        
        self.timeline = QGraphicsRectItem(0, len(self.model.layers) * self.scale_factor_y, 100000, self.timeline_height)  # Height of 50 pixels
        self.timeline.setBrush(QBrush(QColor("#008080")))  # Ruby Red Color
        self.timeline.setPen(QPen(QColor("#00A080"), 2))
        self.timeline.setZValue(0)  # Ensure timeline is above other items
      #  self.scene.addItem(self.timeline)

        # Add timeline label
        timeline_label = QGraphicsTextItem("Timeline")
        timeline_label.setDefaultTextColor(QColor("#008080"))
        timeline_label.setFont(QFont("Comic Sans MS", 14, QFont.Bold))
        timeline_label.setPos(10, len(self.model.layers) * self.scale_factor_y + 1000)
       # self.scene.addItem(timeline_label)

        # Add time markers every second
        total_duration = max(
            (clip.start_time + clip.duration)
            for layer in self.model.layers
            for clip in layer.clips
        ) if any(layer.clips for layer in self.model.layers) else 0
        for i in range(int(total_duration) + 1):
            x = i * self.scale_factor_x
            marker = QGraphicsRectItem(x, len(self.model.layers) * self.scale_factor_y + 0, 1, 90)
            marker.setBrush(QBrush(QColor("#444444")))
            marker.setPen(QPen(Qt.NoPen))

            marker.setZValue(3)
            #self.scene.addItem(marker)

            # Add time label
            time_label = QGraphicsTextItem(f"{i}s")
            time_label.setDefaultTextColor(QColor("#ffffff"))
            time_label.setFont(QFont("Comic Sans MS", 10))
            time_label.setPos(x + 2, len(self.model.layers) * self.scale_factor_y + 5)
            #self.scene.addItem(time_label)

        # Adjust scene rect to include timeline
        #self.scene.setSceneRect(0, 0, 100000, (len(self.model.layers) * self.scale_factor_y) + 50)
       
    # ------------------ Tempo Management Methods ------------------

    def update_tempo(self, value):
        """Update tempo and redraw timeline accordingly."""
        self.tempo = value
        self.sixteenth_note_duration = 60 / (self.tempo * 4)  # Duration of a 16th note in seconds
        self.draw_timeline()

    # ------------------ Settings Placeholder ------------------







    def open_settings(self):
        """Open a settings dialog to change the background color, image, or GIF video of the active layer."""
        if self.active_layer is None:
            QMessageBox.warning(self, "No Active Layer", "Please select a layer to change settings.")
            return

        # Prompt user for background choice: color, image, or gif video
        choice, ok = QInputDialog.getItem(self, "Choose Background Type", "Select background type:",
                                        ["Color", "Image", "GIF Video"], 0, False)

        if ok:
            if choice == "Color":
                # Open color picker to select new background color for the active layer
                color = QColorDialog.getColor()
                if color.isValid():
                    self.active_layer.color = color.name()  # Update the active layer's color

                    # Apply the selected color to the background of the QGraphicsView
                    self.view.setStyleSheet(f"""
                        background-color: {self.active_layer.color};
                        border: 2px solid #150f18;
                        border-radius: 15px;
                    """)

                    # Update lane visuals with the new color
                    for lane in self.active_layer.lanes:
                        lane['rect'].setBrush(QBrush(QColor(self.active_layer.color)))

            elif choice == "Image":
                # Open file picker to select an image
                image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
                if image_path:
                    # Set image as background for the view
                    self.view.setStyleSheet(f"""
                        background-image: url({image_path});
                        border: 2px solid #150f18;
                        border-radius: 15px;
                        background-repeat: no-repeat;
                        background-position: center;
                    """)
            elif choice == "GIF Video":
                # Open file picker to select a GIF video
                gif_path, _ = QFileDialog.getOpenFileName(self, "Select GIF", "", "GIF Files (*.gif)")
                if gif_path:
                    # Use QMovie to load the GIF
                    gif_movie = QMovie(gif_path)

                    # Create QLabel to hold the GIF, positioned at the back of the scene
                    if not hasattr(self, 'gif_item'):
                        self.gif_item = QLabel()
                        self.scene.addWidget(self.gif_item)

                    self.gif_item.setMovie(gif_movie)
                    gif_movie.start()

                    # Resize the GIF to cover the entire background of the scene
                    self.gif_item.setGeometry(self.view.viewport().rect())
                    self.gif_item.setScaledContents(True)

                    # Set the GIF's Z-value lower to ensure it stays in the background
                    self.gif_item.lower()  # Keep it behind other elements

                    # Update the Z-values of lanes and clips to ensure they're above the GIF
                    for layer in self.model.layers:
                        for lane in layer.lanes:
                            lane['rect'].setZValue(1)  # Ensure lanes are above the background
                        for clip in layer.clips:
                            for item in self.scene.items():
                                if isinstance(item, DraggableClip) and item.clip.id == clip.id:
                                    item.setZValue(2)  # Ensure clips are above the lanes










    # ------------------ Event Handling ------------------

    def handle_key_press(self, event):
        """Handle keyboard shortcuts for playback controls."""
        if event.key() == Qt.Key_H:
            # Toggle the visibility of the control panel
            self.control_panel.setVisible(not self.control_panel.isVisible())

            # Check if the GIF item exists and resize it when "H" is pressed
            if hasattr(self, 'gif_item'):
                if self.control_panel.isVisible():
                    # If control panel is visible, resize the GIF to its normal size
                    self.gif_item.setGeometry(self.view.viewport().rect())
                else:
                    # If control panel is hidden, expand the GIF to fill the larger area
                    expanded_rect = self.view.viewport().rect()
                    expanded_rect.setWidth(expanded_rect.width() + 300)  # Increase width to fill the area where control panel was
                    self.gif_item.setGeometry(expanded_rect)

        elif event.key() == Qt.Key_F:
            # Toggle fullscreen mode for just the GIF, hiding all unnecessary UI
            if self.toolbar.isVisible():
                # Hide the toolbar and control panel
                self.toolbar.setVisible(False)
                self.control_panel.setVisible(False)

                # Resize the GIF to cover the entire window
                if hasattr(self, 'gif_item'):
                    self.gif_item.setGeometry(self.rect())  # Resize to fill the entire window
                    self.gif_item.raise_()  # Ensure the GIF is at the top layer

                # Adjust view for fullscreen mode, but keep lanes and clips visible
                self.view.setStyleSheet("background-color: transparent;")  # Transparent background to see GIF
                self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            else:
                # Exit fullscreen: show toolbar and control panel again
                self.toolbar.setVisible(True)
                self.control_panel.setVisible(True)

                # Resize the GIF back to its default position
                if hasattr(self, 'gif_item'):
                    self.gif_item.setGeometry(self.view.viewport().rect())  # Resize the GIF to fit within the viewport

                # Restore the view scrollbars and background color
                self.view.setStyleSheet("background-color: #FFFFFF;")
                self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
                self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        elif event.key() == Qt.Key_P:
            if not self.is_playing:
                self.play()
            else:
                self.pause()

        elif event.key() == Qt.Key_Space:
            self.stop()

        else:
            super(QGraphicsView, self.view).keyPressEvent(event)


    def mousePressEvent(self, event):
        """Handle mouse press events to select clips."""
        super().mousePressEvent(event)
        # Translate the global mouse position to the scene's coordinates
        view_pos = self.view.mapFromGlobal(event.globalPos())
        scene_pos = self.view.mapToScene(view_pos)
        item = self.scene.itemAt(scene_pos, self.view.transform())
        if isinstance(item, DraggableClip):
            self.update_clip_properties(item.clip)
        else:
            self.properties_display.setText("Select a clip to see properties.")

    # ------------------ Save and Load Session Methods ------------------

    def save_session(self):
        """Save the current project session to a JSON file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Session", "", "JSON Files (*.json)", options=options)
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    json.dump(self.model.to_dict(), file, indent=4)
                QMessageBox.information(self, "Success", "Session saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save session:\n{e}")


    def load_session(self):
        """Load a project session from a JSON file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Session", "", "JSON Files (*.json)", options=options)
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)
                loaded_project = Project.from_dict(data)
                self.apply_loaded_project(loaded_project)
                QMessageBox.information(self, "Success", "Session loaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load session:\n{e}")

    def apply_loaded_project(self, loaded_project: Project):
        """Apply the loaded project to the current view and model."""
        # Stop playback if active
        self.stop()

        # Clear current scene and model
        self.clear_scene()
        self.model = loaded_project

        # Update next_id to prevent ID conflicts
        if self.model.layers:
            max_id = max(
                (clip.id for layer in self.model.layers for clip in layer.clips),
                default=0
            )
            self.model.next_id = max_id + 1
        else:
            self.model.next_id = 1

        # Reinitialize layers, lanes, and clips
        self.layer_list.blockSignals(True)
        self.layer_list.clear()

        for layer in self.model.layers:
            # Add layer to layer list
            item = QListWidgetItem(layer.name)
            item.setCheckState(Qt.Checked if layer.visible else Qt.Unchecked)
            item.setData(Qt.UserRole, layer)
            self.layer_list.addItem(item)

            # Set active layer to the first one
            if self.active_layer is None:
                self.active_layer = layer

            # Add lanes visually
            for lane in layer.lanes:
                self.add_lane_visual_loaded(layer, lane['name'])

            # Add clips visually
            for clip in layer.clips:
                self.add_graphics_clip(clip)

        self.layer_list.blockSignals(False)
        self.update_layer_list()

        # Redraw timeline
        self.draw_timeline()



    def add_lane_visual_loaded(self, layer: Layer, lane_name: str):
        """Add lanes when loading a session."""
        lane_height = 100
        lane_number = len(layer.lanes)  # Use lane index
        lane_width = 100000  # Extremely large to simulate infinity
        rect = QGraphicsRectItem(0, lane_number * lane_height, lane_width, lane_height)
        rect.setBrush(QBrush(QColor(layer.color)))

        rect.setPen(QPen(QColor("#e0e0e0"), 2))

        rect.setZValue(-1)  # Ensure lanes are beneath clips but above timeline
        rect.setVisible(layer.visible)
        self.scene.addItem(rect)

        # Add lane label
        label = QGraphicsTextItem(lane_name)
        label.setDefaultTextColor(QColor("#e0e0e0"))  # Ruby Red Text
        label.setFont(QFont("Times New Roman", 12, QFont.Bold))
        label.setPos(10, lane_number * lane_height + (lane_height - label.boundingRect().height()) / 2)
        label.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        label.setVisible(layer.visible)
        self.scene.addItem(label)

        # Update lane information with graphical items
        lane_index = lane_number  # Assuming lanes are added in order
        layer.lanes[-1]['rect'] = rect
        layer.lanes[-1]['label'] = label

        # Connect context menu for lanes
        label.mouseDoubleClickEvent = self.edit_lane_properties_factory(label, layer, lane_number + 1)
        label.setCursor(Qt.PointingHandCursor)


    def add_lane_visual(self, layer: Layer, lane_name: str):
        lane_height = 100
        lane_number = len(layer.lanes) + 1
        lane_width = 100000
        rect = QGraphicsRectItem(0, (lane_number - 1) * lane_height, lane_width, lane_height)
        rect.setBrush(QBrush(QColor(layer.color)))  # Use layer's color for lane
        rect.setPen(QPen(QColor("#e0e0e0"), 2))  # Border color
        rect.setZValue(-1)
        rect.setVisible(layer.visible)
        self.scene.addItem(rect)


        # Add lane label
        label = QGraphicsTextItem(lane_name)
        label.setDefaultTextColor(QColor("#202040"))  # Ruby Red Text
        label.setFont(QFont("Times New Roman", 12, QFont.Bold))
        label.setPos(10, (lane_number - 1) * lane_height + (lane_height - label.boundingRect().height()) / 2)
        label.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsFocusable)
        label.setVisible(layer.visible)
        self.scene.addItem(label)

        # Store lane information in the model with 'rect' and 'label'
        layer.lanes.append({'rect': rect, 'label': label, 'name': lane_name})

        # Connect context menu for lanes
        label.mouseDoubleClickEvent = self.edit_lane_properties_factory(label, layer, lane_number)
        label.setCursor(Qt.PointingHandCursor)


    def clear_scene(self):
        """Remove all items from the scene."""
        for item in self.scene.items():
            self.scene.removeItem(item)
        self.scene.clear()



    # ------------------ Additional Helper Methods ------------------

    def add_clip_to_loaded_project(self, clip: TextClip):
        """Add clip to loaded project."""
        self.model.clips.append(clip)
        self.add_graphics_clip(clip)

    # ------------------ End of FancyPaperdawView Class ------------------


# ------------------ Main Application ------------------

def main():
    app = QApplication(sys.argv)

    # Set Application Style
    app.setStyle("Fusion")

    # Dark Palette with Ruby Accents
    palette = app.palette()
    palette.setColor(app.palette().Window, QColor("#e0e0e0"))
    palette.setColor(app.palette().WindowText, QColor("#e0e0e0"))
    palette.setColor(app.palette().Base, QColor("#e0e0e0"))
    palette.setColor(app.palette().AlternateBase, QColor("#e0e0e0"))
    palette.setColor(app.palette().ToolTipBase, QColor("#e0e0e0"))
    palette.setColor(app.palette().ToolTipText, QColor("#e0e0e0"))
    palette.setColor(app.palette().Text, QColor("#000000"))
    palette.setColor(app.palette().Button, QColor("#e0e0e0"))
    palette.setColor(app.palette().ButtonText, QColor("#FFFFFF"))
    palette.setColor(app.palette().BrightText, QColor("#FFFFFF"))
    palette.setColor(app.palette().Link, QColor("#e0e0e0"))
    palette.setColor(app.palette().Highlight, QColor("#e0e0e0"))
    palette.setColor(app.palette().HighlightedText, QColor("#e0e0e0"))
    app.setPalette(palette)

    # Initialize Model
    project = Project()

    # Initialize View
    window = FancyPaperdawView(project)
    window.show()

    # Do not add any initial clips or lanes

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
