from B4_Automata import Automata, open_image
import graphviz
import os
from PIL import Image
from pathlib import Path

global DIR
DIR = os.path.dirname(os.path.realpath(__file__))

def scale(image, max_size, method=Image.LANCZOS):
    """
    Takes an image, a max_size tuple and a method.
    The function resizes the image to the max_size keeping the aspect ratio
    and places it in center of white 'max_size' image.

    taken from : https://gist.github.com/fabeat/6621507?permalink_comment_id=2378878#gistcomment-2378878

    :param image: Pass the image to be resized
    :param max_size: Set the maximum size of the image
    :param method: Specify the resampling filter
    :return: A scaled image
    """
    image.thumbnail(max_size, method)
    offset = (int((max_size[0] - image.size[0]) / 2), int((max_size[1] - image.size[1]) / 2))
    back = Image.new("RGB", max_size, "white")
    back.paste(image, offset)

    return back


class AutomataAnimation:
    try:
        os.mkdir(f"out/anim")
    except FileExistsError:
        ...
    except FileNotFoundError:
        ...

    @staticmethod
    def standardize_animation(automata: Automata, view: bool = False):
        """
        Takes an automata and a boolean value as arguments.

        :param automata: Automata: Get the automata that is going to be standardized
        :param view: bool: Determine whether the animation should be opened after it has been created
        :return: A string
        """
        try:
            os.mkdir(Path(DIR) / Path(f"out/anim/{automata.output}"))
        except FileExistsError:
            ...

        file = f'out/anim/{automata.output}/{automata.output}'

        file_names = [f'{DIR}/{file}_base.png',
                      f'{DIR}/{file}_std.png']

        graphviz.Source(automata.to_dot_format()) \
            .render(outfile=f'{file_names[0]}', format='png', view=False)

        graphviz.Source(automata.get_standard().to_dot_format()) \
            .render(outfile=f'{file_names[1]}', format='png', view=False)

        images = [Image.open(fn) for fn in file_names]
        m = max([im.size for im in images])
        images = [scale(img, m) for img in images]

        images[0].save(Path(DIR) / Path(f"out/anim/{automata.output}/strandardize.gif"),
                       save_all=True, append_images=images[1:], optimize=False, duration=2000, loop=0)

        if view:
            open_image(Path(DIR) / Path(f"out/anim/{automata.output}/strandardize.gif"))

        for f in file_names:
            os.remove(Path(DIR) / Path(f))
            os.remove(Path(DIR) / Path(f.replace("png", "gv")))

        return ''

    @staticmethod
    def determinize_animation(automata: Automata, duration: int = 2, view=False):
        """
        Takes an automata and a duration as input.

        :param automata: Automata: Get the automata object
        :param duration: int: Set the duration of each image in the gif
        :param view: Open the image in a new window
        :return: A string
        """
        try:
            os.mkdir(f"out/anim/{automata.output}")
        except FileExistsError:
            ...

        steps: list[object | Automata] = automata.get_determinized(step=True)
        steps = [automata] + steps

        file = f'out/anim/{automata.output}/{automata.output}'

        file_names = [f'{DIR}/{file}_{i}.png' for i in range(len(steps))]

        for f, s in zip(file_names, steps):
            graphviz.Source(s.to_dot_format()) \
                .render(outfile=f'{f}', format='png', view=False)

        images = [Image.open(fn) for fn in file_names]
        m = max([im.size for im in images])
        images = [scale(img, m) for img in images]

        images[0].save(Path(DIR) / Path(f"out/anim/{automata.output}/determinize.gif"),
                       save_all=True, append_images=images[1:], optimize=False, duration=duration * 1000, loop=0)

        if view:
            open_image(Path(DIR) / Path(f"out/anim/{automata.output}/determinize.gif"))

        for f in file_names:
            os.remove(Path(DIR) / Path(f))
            os.remove(Path(f.replace("png", "gv")))

        return ''
