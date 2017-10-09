import argparse
import os
import random
import uuid
import time

from vis_image import ImageVisualizer
import utils

TMP_DIR = "tmp/"
IMAGES_DIR = "tmp/images/"
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

class ProjectVisualizer:

    def __init__(self, project, config, MAX=100):
        self.project = project
        self.image_visualizer = ImageVisualizer(project, config)
        self.MAX = MAX

        fname = "{}_{}.html".format(project, int(time.time()))
        self.output_path = os.path.join(TMP_DIR, fname)

        self.init_output_file(config)

    def init_output_file(self, config):
        head = str(config)
        body = ""
        html = "<html><head>" + head + "</head><body>" + body + "</body></html>"
        with open(self.output_path, 'w') as f:
            f.write(html)

        # Print link to output file
        root = "/data/vision/oliva/scenedataset/"
        abs_path = os.path.abspath(self.output_path)
        rel_path = os.path.relpath(abs_path, root)
        print "http://places.csail.mit.edu/{}".format(rel_path)

    def visualize_images(self, im_list):
        for n, line in enumerate(im_list[:self.MAX]):
            print n, line
            self.add_image_section(line)

    def add_image_section(self, line):
        im = line.split()[0]
        paths = self.image_visualizer.visualize(im)

        image_tags = []
        order = ["image", "prob_mask", "category_mask", "ground_truth", "diff"]
        for key in order:
            if key in paths:
                tag = self.get_image_tag(paths[key])
                image_tags.append(tag)
                del paths[key]
        # Add the rest
        for key in paths:
            tag = self.get_image_tag(paths[key])
            image_tags.append(tag)

        # Build section
        title = "{} {}".format(self.project, line)
        imgs = ' '.join(image_tags)
        section = "<br><br>{}<br><br>{}".format(title, imgs)

        # Append to body
        with open(self.output_path, 'r') as f:
            html = f.read()
        new_html = html.replace("</body>", "{}</body>".format(section))
        with open(self.output_path, 'w') as f:
            f.write(new_html)

    def get_image_tag(self, path):
        if os.path.isabs(path):
            # Symlink into tmp image directory
            path = self.symlink(path)

        path = os.path.relpath(path, os.path.dirname(self.output_path))
        return "<img src=\"{}\" height=\"256px\">".format(path)

    def symlink(self, path):
        fn = "{}.jpg".format(uuid.uuid4().hex)
        dst = os.path.join(IMAGES_DIR, fn)
        os.symlink(path, dst)
        return dst

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', type=str, required=True, help="Project name")
    parser.add_argument("--prediction", type=str, required=True, help="")
    parser.add_argument('-r', '--randomize', action='store_true', default=False, help="Randomize image list")
    parser.add_argument('-i', '--im_list', type=str, help="Specific image list")
    parser.add_argument('-e', '--evaluation', type=str, help="Evaluation matrix")
    parser.add_argument('-n', '--number', type=int, default=10, help="Number of images")
    args = parser.parse_args()
    
    config = utils.get_config(args.project)
    if args.prediction is not None:
        config["pspnet_prediction"] = args.prediction
        config["evaluation"] = args.evaluation

    im_list = None
    if not args.im_list:
        # Open default image list
        im_list = utils.open_im_list(config["im_list"])
    else:
        # Open specific image list
        im_list = utils.open_im_list(args.im_list)

    if args.randomize:
        # Shuffle image list
        random.seed(3)
        random.shuffle(im_list)

    vis = ProjectVisualizer(args.project, config, MAX=args.number)
    vis.visualize_images(im_list)

