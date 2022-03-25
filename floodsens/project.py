import floodsens.preprocessing as preprocessing
import floodsens.inference as inference
from pathlib import Path


class Project():
    def __init__(self, root, zip_path, tile_dir=None, inferred_dir=None, 
                    inferred_path=None, model_path=None, cuda=True):
        self.root = Path(root)
        self.zip_path = Path(zip_path) # TODO How to handle multiple Sentinel images?

        if model_path is None: self.model_path = None
        else: self.model_path = model_path

        if tile_dir is None: self.tile_dir = None
        else: self.tile_dir = Path(tile_dir)
        
        if inferred_dir is None: self.inferred_dir = None
        else: self.inferred_dir = Path(inferred_dir)

        if inferred_path is None: self.inferred_path = None
        else: self.inferred_path = Path(inferred_path)

        self.cuda = cuda

    def __repr__(self):
        if self.tile_dir is None: tile_dir = "(not set)" 
        else: tile_dir = self.tile_dir
        if self.model_path is None: model_path = "(not set)"
        else: model_path = self.model_path
        if self.inferred_dir is None: inferred_dir = "(not set)"
        else: inferred_dir = self.inferred_dir
        if self.inferred_path is None: inferred_path = "(not set)"
        else: inferred_path = self.inferred_path
        

        repr_str = f'Project Folder:\t\t{self.root}\n'
        repr_str +=f'Sentinel Archive:\t{self.zip_path}\n'
        repr_str +=f'Model:\t\t\t{model_path}\n'
        repr_str +=f'Preprocessed Tiles:\t{tile_dir}\n'
        repr_str +=f'Inferred Tiles:\t\t{inferred_dir}\n'
        repr_str +=f'Inferred Map:\t\t{inferred_path}'

        return repr_str

    @classmethod
    def from_folder(cls, root, model_path=None):
        zip_path = list((Path(root)/'zip').iterdir())[0] # TODO DO BETTER
        project = cls(root, zip_path)

        project.model_path = model_path
        
        tile_dir = Path(root)/'tiles'/'stacked'
        if not tile_dir.exists(): tile_dir = None
        project.tile_dir = tile_dir
        
        inferred_dir = Path(root)/'tiles'/'out_tiles'
        if not inferred_dir.exists(): inferred_dir = None
        project.inferred_dir = inferred_dir

        inferred_path = Path(root)/'merged_map.tif'
        if not inferred_path.exists(): inferred_path = None

        return project

    def default_preprocessing(self):
        self.tile_dir = preprocessing.run_default_preprocessing(self.root, self.zip_path)

    def choose_model(self):
        model_paths = [x for x in Path('models').iterdir() if x.is_dir()]       
        print("Available models:\n", *[f"\t{k+1}) {x.name}\n" for k, x in enumerate(model_paths)])
        model_idx = int(input("Type Number of model to load it\n"))
        model_path = model_paths[int(model_idx)-1]/"model.pth.tar"
        self.model_path = model_path

    def load_model(self, model_path):
        self.model_path = model_path

    def inference(self):
        self.inferred_dir = inference.run_inference(self.model_path, self.tile_dir, cuda=self.cuda)

    def save_map(self, out_path=None):
        out_dir = Path(self.root)/'tiles'/'map'
        if out_path is None: out_path = Path(self.root)/'merged_map.tif'
        self.inferred_path = inference.create_map(self.tile_dir, 
                                                    self.inferred_dir, 
                                                    out_dir=out_dir, 
                                                    out_path=out_path)
        