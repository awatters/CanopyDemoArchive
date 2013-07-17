print "hello world"
from skimpyGimpy import canvas
c = canvas.Canvas()

# set the foreground color to a light blue
c.setColor(99,99,0xff)

# set the background color to a dark green
c.setBackgroundColor(10,50,0)

# name a font "propell" and associate it with a BDF font file
c.addFont("propell", "fonts/mlmfonts/propell.bdf")

# set the current font to "propell" with scale 2.0 and
# pixel radius 1.3
c.setFont("propell", 2.0, 1.3)

# draw some text
#c.addText(0,0, "Hello PNG World")
c.addText(0,60, "Hello")
c.addText(0,30, "PNG")
c.addText(0,0, "World")

c.dumpToPNG("HelloWorld.png")

import matplotlib.image as mpimg

img=mpimg.imread('HelloWorld.png')

import matplotlib.pyplot as plt
imgplot = plt.imshow(img)
plt.show()
