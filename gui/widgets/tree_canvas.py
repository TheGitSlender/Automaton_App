
import math
from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsView, QGraphicsItem, 
    QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
    QGraphicsPathItem, QWidget, QMenu, QAction
)
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QFont


class AutomataCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.automaton = None
        self.state_items = {}
        self.transition_items = []
        
        # Create scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Set rendering options
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.TextAntialiasing)
        
        # Enable drag view
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        
        # Set dimensions
        self.setMinimumSize(400, 300)
        
        # Styling
        self.state_radius = 30
        self.state_color = QColor(240, 240, 240)
        self.state_border_color = QColor(0, 0, 0)
        self.state_selected_color = QColor(200, 230, 255)
        self.transition_color = QColor(0, 0, 0)
        self.font = QFont("Arial", 10)
        
        # Initialize canvas
        self.clear_canvas()
    
    def clear_canvas(self):
        self.scene.clear()
        self.state_items = {}
        self.transition_items = []
    
    def update_automaton(self, automaton):
        self.automaton = automaton
        self.clear_canvas()
        
        if not automaton:
            return
        
        # Add states
        self.add_states()
        
        # Add transitions
        self.add_transitions()
    
    def add_states(self):
        if not self.automaton:
            return
        
        # Calculate positions in a circle layout
        num_states = len(self.automaton.states)
        center_x = 0
        center_y = 0
        radius = max(150, num_states * 50)
        
        for i, (state_id, state) in enumerate(self.automaton.states.items()):
            # Calculate position on circle
            angle = 2 * math.pi * i / num_states
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Create state
            self.add_state(state, x, y)
    
    def add_state(self, state, x, y):
        # Create state ellipse
        ellipse_item = QGraphicsEllipseItem(
            -self.state_radius, -self.state_radius,
            2 * self.state_radius, 2 * self.state_radius
        )
        ellipse_item.setBrush(QBrush(self.state_color))
        ellipse_item.setPen(QPen(self.state_border_color, 2))
        ellipse_item.setPos(x, y)
        ellipse_item.setFlag(QGraphicsItem.ItemIsSelectable)
        ellipse_item.setData(0, state.name)  # Store state name as item data
        self.scene.addItem(ellipse_item)
        
        # Create state name text
        text_item = QGraphicsTextItem(state.name)
        text_item.setFont(self.font)
        
        # Center the text in the state
        text_width = text_item.boundingRect().width()
        text_height = text_item.boundingRect().height()
        text_x = x - text_width / 2
        text_y = y - text_height / 2
        text_item.setPos(text_x, text_y)
        self.scene.addItem(text_item)
        
        # If initial state, add an arrow
        if state.is_initial:
            # Create the initial state arrow pointing to the left side of the state
            arrow_length = self.state_radius * 2  # Length of the arrow shaft
            
            # Calculate arrow start point, further away from the circle
            arrow_start_x = x - self.state_radius - arrow_length
            arrow_start_y = y
            
            # Calculate arrow end point, exactly at the circle's edge
            arrow_end_x = x - self.state_radius 
            arrow_end_y = y
            
            # Create the arrow path
            arrow_path = QPainterPath()
            arrow_path.moveTo(arrow_start_x, arrow_start_y)
            arrow_path.lineTo(arrow_end_x, arrow_end_y)
            
            arrow_item = QGraphicsPathItem(arrow_path)
            arrow_item.setPen(QPen(self.transition_color, 2))
            self.scene.addItem(arrow_item)
            
            # Add arrowhead - make it more visible
            arrowhead_size = 10
            arrowhead_path = QPainterPath()
            arrowhead_path.moveTo(arrow_end_x, arrow_end_y)
            arrowhead_path.lineTo(arrow_end_x - arrowhead_size, arrow_end_y - arrowhead_size)
            arrowhead_path.lineTo(arrow_end_x - arrowhead_size, arrow_end_y + arrowhead_size)
            arrowhead_path.closeSubpath()
            
            arrowhead_item = QGraphicsPathItem(arrowhead_path)
            arrowhead_item.setPen(QPen(self.transition_color, 2))
            arrowhead_item.setBrush(QBrush(self.transition_color))
            self.scene.addItem(arrowhead_item)
        
        # If final state, add an inner circle
        if state.is_final:
            final_ellipse = QGraphicsEllipseItem(
                -self.state_radius * 0.7, -self.state_radius * 0.7,
                2 * self.state_radius * 0.7, 2 * self.state_radius * 0.7
            )
            final_ellipse.setPen(QPen(self.state_border_color, 2))
            final_ellipse.setPos(x, y)
            self.scene.addItem(final_ellipse)
        
        # Store the state item
        self.state_items[state.name] = {
            'item': ellipse_item,
            'pos': (x, y),
            'state': state
        }
    
    def add_transitions(self):
        if not self.automaton:
            return
        
        for transition in self.automaton.transitions:
            src_name = transition.src.name
            dest_name = transition.dest.name
            
            # Get source and destination positions
            if src_name in self.state_items and dest_name in self.state_items:
                src_pos = self.state_items[src_name]['pos']
                dest_pos = self.state_items[dest_name]['pos']
                
                # Add the transition
                self.add_transition(src_pos, dest_pos, transition.symbol, src_name == dest_name)
    
    def add_transition(self, src_pos, dest_pos, symbol, is_self_loop=False):
        """
        Add a transition to the canvas.
        
        Args:
            src_pos: Source position (x, y)
            dest_pos: Destination position (x, y)
            symbol: Transition symbol
            is_self_loop: Whether this is a self-loop
        """
        src_x, src_y = src_pos
        dest_x, dest_y = dest_pos
        
        if is_self_loop:
            # Count existing self-loops on this state to position this one
            existing_self_loops = 0
            for item in self.transition_items:
                if item['src'] == src_pos and item['dest'] == src_pos:
                    existing_self_loops += 1
            
            # Base angle for positioning self-loops around the state
            base_angle = math.pi / 2  # Start from top (π/2)
            angle_step = math.pi / 6  # 30 degrees separation
            
            # Calculate position for this loop based on number of existing loops
            loop_angle = base_angle - angle_step * existing_self_loops
            if existing_self_loops > 0 and existing_self_loops % 2 == 0:
                # Alternate sides for even numbered loops
                loop_angle = base_angle + angle_step * existing_self_loops / 2
            elif existing_self_loops > 1 and existing_self_loops % 2 == 1:
                # Alternate sides for odd numbered loops (past the first one)
                loop_angle = base_angle - angle_step * (existing_self_loops+1) / 2
            
            # Calculate loop center position
            distance = self.state_radius * 1.5
            loop_center_x = src_x + distance * math.cos(loop_angle)
            loop_center_y = src_y - distance * math.sin(loop_angle)
            
            # Size of the loop
            loop_radius = self.state_radius * 0.8
            
            # Draw the loop
            loop_path = QPainterPath()
            loop_path.addEllipse(loop_center_x - loop_radius, loop_center_y - loop_radius, 
                               loop_radius * 2, loop_radius * 2)
                               
            loop_item = QGraphicsPathItem(loop_path)
            loop_item.setPen(QPen(self.transition_color, 2))
            self.scene.addItem(loop_item)
            
            # Add text near the loop
            text_item = QGraphicsTextItem(symbol)
            text_item.setFont(self.font)
            text_width = text_item.boundingRect().width()
            text_height = text_item.boundingRect().height()
            
            # Position text based on loop position
            text_angle = loop_angle  # Text position at the same angle
            text_distance = loop_radius * 1.5
            text_x = loop_center_x + text_distance * math.cos(text_angle) - text_width/2
            text_y = loop_center_y - text_distance * math.sin(text_angle) - text_height/2
            text_item.setPos(text_x, text_y)
            self.scene.addItem(text_item)
            
            # Calculate arrowhead position - pointing at an angle toward the state
            arrow_angle = loop_angle + math.pi  # Point in the opposite direction of the loop position
            arrow_x = loop_center_x + loop_radius * math.cos(arrow_angle)
            arrow_y = loop_center_y - loop_radius * math.sin(arrow_angle)
            
            self.add_arrowhead(arrow_x, arrow_y, arrow_angle)
        else:
            # Calculate direction vector
            dx = dest_x - src_x
            dy = dest_y - src_y
            length = math.sqrt(dx * dx + dy * dy)
            
            if length < 1e-6:  # Avoid division by zero
                return
                
            # Normalize
            dx /= length
            dy /= length
            
            # Calculate start and end points to be on the edge of the circles
            start_x = src_x + dx * self.state_radius
            start_y = src_y + dy * self.state_radius
            end_x = dest_x - dx * self.state_radius
            end_y = dest_y - dy * self.state_radius
            
            # Draw curved paths for transitions between the same states
            offset = 20  # Controls the curvature
            path = QPainterPath()
            path.moveTo(start_x, start_y)
            
            # Check if there are already transitions between these states
            existing_count = 0
            for item in self.transition_items:
                if item['src'] == src_pos and item['dest'] == dest_pos:
                    existing_count += 1
                elif item['src'] == dest_pos and item['dest'] == src_pos:
                    existing_count += 1
            
            # If there are existing transitions, offset this one
            if existing_count > 0:
                # Calculate perpendicular vector
                perp_x = -dy
                perp_y = dx
                
                # Control point for quadratic curve
                control_x = (start_x + end_x) / 2 + perp_x * offset * (existing_count + 1)
                control_y = (start_y + end_y) / 2 + perp_y * offset * (existing_count + 1)
                
                path.quadTo(control_x, control_y, end_x, end_y)
                
                # Position for the text (next to the control point)
                text_x = control_x + perp_x * 5
                text_y = control_y + perp_y * 5
                
                # Calculate angle for arrowhead
                angle = math.atan2(end_y - control_y, end_x - control_x)
            else:
                # Draw a straight line
                path.lineTo(end_x, end_y)
                
                # Position for the text (midpoint of the line)
                text_x = (start_x + end_x) / 2 + 5
                text_y = (start_y + end_y) / 2 - 15
                
                # Calculate angle for arrowhead
                angle = math.atan2(dy, dx)
            
            # Draw the path
            path_item = QGraphicsPathItem(path)
            path_item.setPen(QPen(self.transition_color, 2))
            self.scene.addItem(path_item)
            
            # Add the symbol text
            text_item = QGraphicsTextItem(symbol)
            text_item.setFont(self.font)
            text_item.setPos(text_x, text_y)
            self.scene.addItem(text_item)
            
            # Add arrowhead
            self.add_arrowhead(end_x, end_y, angle)
        
        # Store the transition
        self.transition_items.append({
            'src': src_pos,
            'dest': dest_pos,
            'symbol': symbol
        })
        
    def add_arrowhead(self, x, y, angle):
        """
        Add an arrowhead to the canvas.
        
        Args:
            x, y: Position of the arrowhead tip
            angle: Angle of the arrow in radians
        """
        size = 10  # Size of the arrowhead
        
        # Calculate points for the arrowhead
        p1_x = x - size * math.cos(angle - 0.3)
        p1_y = y - size * math.sin(angle - 0.3)
        p2_x = x - size * math.cos(angle + 0.3)
        p2_y = y - size * math.sin(angle + 0.3)
        
        # Create the arrowhead path
        path = QPainterPath()
        path.moveTo(x, y)  # Tip of the arrow
        path.lineTo(p1_x, p1_y)
        path.lineTo(p2_x, p2_y)
        path.closeSubpath()
        
        # Create the item
        arrowhead_item = QGraphicsPathItem(path)
        arrowhead_item.setPen(QPen(self.transition_color, 2))
        arrowhead_item.setBrush(QBrush(self.transition_color))
        self.scene.addItem(arrowhead_item)
    
    def wheelEvent(self, event):
        """
        Handle wheel event for zooming.
        
        Args:
            event: The wheel event
        """
        factor = 1.1
        if event.angleDelta().y() < 0:
            factor = 0.9
        
        self.scale(factor, factor)
    
    def contextMenuEvent(self, event):
        """
        Handle context menu event.
        
        Args:
            event: The context menu event
        """
        menu = QMenu(self)
        reset_zoom_action = menu.addAction("Reset Zoom")
        fit_action = menu.addAction("Fit View")
        
        selected_action = menu.exec_(self.mapToGlobal(event.pos()))
        
        if selected_action == reset_zoom_action:
            self.resetTransform()
        elif selected_action == fit_action:
            self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
    
    def clear_automaton(self):
        """
        Clear the automaton and canvas.
        """
        self.automaton = None
        self.clear_canvas() 