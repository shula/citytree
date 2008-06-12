# -*- coding:utf-8 -*-
import os, tempfile, cairo

def text_bounds(text, size, font="Sans", weight=cairo.FONT_WEIGHT_NORMAL, style=cairo.FONT_SLANT_NORMAL):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
    context = cairo.Context(surface)
    context.select_font_face(font, style, weight)
    context.set_font_size(size)
    width, height = context.text_extents(text)[2:4]
    return width, height

def render_image(drawer, width, height, filename):
    # We render to a generic Image, being careful not to use colour hinting
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
    font_options = surface.get_font_options()
    font_options.set_antialias(cairo.ANTIALIAS_GRAY)
    context = cairo.Context(surface)
    # Call our drawing function on that context, now.
    drawer(context)
    # Write the PNG data to our tempfile
    surface.write_to_png(filename)
    surface.finish()
    # Now stream that file’s content back to the client
    fo = open(filename)
    data = fo.read()
    fo.close()

def render_title(text, filename, size=60):
    # Get some variables pinned down
    size = int(size) * 3
    font = "Meta"
    width, height = text_bounds(text, size, font)
    def draw(cr):
        import cairo
        # Paint the background white. Replace with 1,1,1,0 for transparent PNGs.
        cr.set_source_rgba(1,1,1,1)
        cr.paint()
        # Some black text
        cr.set_source_rgba(0,0,0,1)
        cr.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(size)
        # We need to adjust by the text’s offsets to center it.
        x_bearing, y_bearing, width, height = cr.text_extents(text)[:4]
        cr.move_to(-x_bearing,-y_bearing)
        # We stroke and fill to make sure thinner parts are visible.
        cr.text_path(text)
        cr.set_line_width(0.5)
        cr.stroke_preserve()
        cr.fill()
    return render_image(draw, width, height, filename)

