"""Custom rounded widgets for a modern UI look."""

import tkinter as tk


class RoundedButton(tk.Canvas):
    """A button with rounded corners, drawn on a Canvas."""

    def __init__(self, parent, text="", command=None,
                 bg_color="#FFD700", fg_color="#012b45",
                 hover_color=None, corner_radius=15,
                 height=40, font=None, **kwargs):
        super().__init__(parent, height=height, highlightthickness=0, **kwargs)

        self._text = text
        self._command = command
        self._bg_color = bg_color
        self._fg_color = fg_color
        self._hover_color = hover_color
        self._corner_radius = corner_radius
        self._height = height
        self._font = font or ('Segoe UI', 10)
        self._state = 'normal'
        self._pressed = False

        self._update_canvas_bg()

        self.bind('<Configure>', self._on_configure)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _update_canvas_bg(self):
        """Match canvas background to the current theme."""
        try:
            style = self.winfo_toplevel().style
            self.configure(bg=style.colors.bg)
        except Exception:
            pass

    def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """Draw a rounded rectangle on the canvas."""
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw(self, override_color=None):
        """Redraw the button."""
        self.delete('all')
        w = self.winfo_width()
        h = self._height
        if w <= 1:
            return

        color = override_color or self._bg_color
        fg = self._fg_color

        if self._state == 'disabled':
            color = self._adjust_color(color, darken=0.4)
            fg = self._adjust_color(fg, darken=0.3)

        r = min(self._corner_radius, h // 2)
        self._rounded_rect(1, 1, w - 1, h - 1, r, fill=color, outline='')
        self.create_text(w / 2, h / 2, text=self._text,
                         fill=fg, font=self._font)

    @staticmethod
    def _adjust_color(color, lighten=0.0, darken=0.0):
        """Lighten or darken a hex color."""
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            if lighten:
                r = min(255, int(r + (255 - r) * lighten))
                g = min(255, int(g + (255 - g) * lighten))
                b = min(255, int(b + (255 - b) * lighten))
            if darken:
                r = max(0, int(r * (1 - darken)))
                g = max(0, int(g * (1 - darken)))
                b = max(0, int(b * (1 - darken)))
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            return color

    def _on_configure(self, _event):
        self._draw()

    def _on_enter(self, _event):
        if self._state != 'disabled':
            hover = self._hover_color or self._adjust_color(self._bg_color, lighten=0.15)
            self._draw(override_color=hover)

    def _on_leave(self, _event):
        self._draw()

    def _on_press(self, _event):
        if self._state != 'disabled':
            self._pressed = True
            pressed_color = self._adjust_color(self._bg_color, darken=0.1)
            self._draw(override_color=pressed_color)

    def _on_release(self, _event):
        if self._pressed and self._state != 'disabled':
            self._pressed = False
            self._draw()
            if self._command:
                self._command()

    def configure(self, **kwargs):
        redraw = False
        if 'text' in kwargs:
            self._text = kwargs.pop('text')
            redraw = True
        if 'bg_color' in kwargs:
            self._bg_color = kwargs.pop('bg_color')
            redraw = True
        if 'fg_color' in kwargs:
            self._fg_color = kwargs.pop('fg_color')
            redraw = True
        if 'state' in kwargs:
            self._state = kwargs.pop('state')
            redraw = True
        if 'command' in kwargs:
            self._command = kwargs.pop('command')
        # Silently ignore ttkbootstrap-specific params
        kwargs.pop('bootstyle', None)
        if kwargs:
            super().configure(**kwargs)
        if redraw:
            self._draw()

    config = configure

    def update_theme_bg(self):
        """Refresh canvas background after theme change."""
        self._update_canvas_bg()
        self._draw()
