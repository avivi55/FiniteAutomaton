from Automata import Automata
import graphviz
import os
from PIL import Image

# STOLEN from : https://gist.github.com/fabeat/6621507?permalink_comment_id=2378878#gistcomment-2378878
def scale(image, max_size, method=Image.ANTIALIAS):
    """
    resize 'image' to 'max_size' keeping the aspect ratio
    and place it in center of white 'max_size' image
    """
    image.thumbnail(max_size, method)
    offset = (int((max_size[0] - image.size[0]) / 2), int((max_size[1] - image.size[1]) / 2))
    back = Image.new("RGB", max_size, "white")
    back.paste(image, offset)

    return back


class AutomataAnimation:
    @staticmethod
    def standardize_animation(automata: Automata):

        try:
            os.mkdir(f"anim")
            os.mkdir(f"anim/{automata.output}")
        except:
            pass

        file = f'anim/{automata.output}/{automata.output}'

        file_names = [f'{file}_base.png',
                      f'{file}_std.png']

        graphviz.Source(automata.to_dot_format()) \
            .render(outfile=f'{file_names[0]}', format='png', view=False)

        graphviz.Source(automata.standardize().to_dot_format()) \
            .render(outfile=f'{file_names[1]}', format='png', view=False)

        images = [Image.open(fn) for fn in file_names]
        m = max([im.size for im in images])
        images = [scale(img, m) for img in images]

        images[0].save(f"anim/{automata.output}/strandardize.gif",
                       save_all=True, append_images=images[1:], optimize=False, duration=2000, loop=0)

        for f in file_names:
            os.remove(f)
            os.remove(f'{f[:-4]}.gv')
