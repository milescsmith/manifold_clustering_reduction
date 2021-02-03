import edifice as ed
from edifice import Label
from edifice import TextInput
from edifice import View

window = View(layout="row")(  # Layout children in a row
    Label("Measurement in meters:"),
    TextInput(""),
    Label("Measurement in feet:"),
)

if __name__ == "__main__":
    ed.App(window).start()
