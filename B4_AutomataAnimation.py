from B4_Automata import Automata, open_image
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
    try:
        os.mkdir(f"anim")
    except FileExistsError:
        ...

    @staticmethod
    def standardize_animation(automata: Automata, view: bool = False):
        try:
            os.mkdir(f"anim/{automata.output}")
        except FileExistsError:
            ...

        file = f'anim/{automata.output}/{automata.output}'

        file_names = [f'{file}_base.png',
                      f'{file}_std.png']

        graphviz.Source(automata.to_dot_format()) \
            .render(outfile=f'{file_names[0]}', format='png', view=False)

        graphviz.Source(automata.get_standard().to_dot_format()) \
            .render(outfile=f'{file_names[1]}', format='png', view=False)

        images = [Image.open(fn) for fn in file_names]
        m = max([im.size for im in images])
        images = [scale(img, m) for img in images]

        images[0].save(f"anim/{automata.output}/strandardize.gif",
                       save_all=True, append_images=images[1:], optimize=False, duration=2000, loop=0)

        if view:
            open_image(f"anim/{automata.output}/strandardize.gif")

        for f in file_names:
            os.remove(f)
            os.remove(f'{f[:-4]}.gv')

        return ''

    @staticmethod
    def determinize_animation(automata: Automata, duration: int = 2, view=False):
        try:
            os.mkdir(f"anim/{automata.output}")
        except FileExistsError:
            ...

        steps: list[object | Automata] = automata.get_determinized(step=True)
        steps = [automata] + steps

        file = f'anim/{automata.output}/{automata.output}'

        file_names = [f'{file}_{i}.png' for i in range(len(steps))]

        for f, s in zip(file_names, steps):
            graphviz.Source(s.to_dot_format()) \
                .render(outfile=f'{f}', format='png', view=False)

        images = [Image.open(fn) for fn in file_names]
        m = max([im.size for im in images])
        images = [scale(img, m) for img in images]

        images[0].save(f"anim/{automata.output}/determinize.gif",
                       save_all=True, append_images=images[1:], optimize=False, duration=duration * 1000, loop=0)

        if view:
            open_image(f"anim/{automata.output}/determinize.gif")

        for f in file_names:
            os.remove(f)
            os.remove(f'{f[:-4]}.gv')

        return ''
