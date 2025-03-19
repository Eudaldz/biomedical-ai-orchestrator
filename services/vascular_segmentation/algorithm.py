import os
import torch
import warnings
from modules.nnUNet.nnunetv2.inference.predict_from_raw_data import nnUNetPredictor
import logging
import nibabel as nib
import shutil
from utils.image import DICOMProcessor

def delete_folder_contents(folder_path):
    """
    Deletes all files and subfolders inside the specified folder.

    :param folder_path: Path to the folder whose contents need to be deleted
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder '{folder_path}' does not exist.")

    # Iterate through all items in the folder
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        try:
            # Remove directory or file
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directory and its contents
            else:
                os.remove(item_path)  # Remove file
        except Exception as e:
            raise IOError(f"Error deleting '{item_path}': {e}")

def run_segmentation(folder_path):

    # Configuración para reducir los mensajes de advertencia y texto innecesario
    logging.basicConfig(level=logging.ERROR)  # Solo mostrar errores importantes
    logging.getLogger("nnunetv2").setLevel(logging.ERROR)
    warnings.filterwarnings("ignore", category=FutureWarning)  # Ignorar FutureWarnings
    warnings.filterwarnings("ignore", module="timm")  # Ignorar advertencias de timm
    warnings.filterwarnings("ignore", module="tqdm")
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Reducir verbosidad de TensorFlow si está presente

    torch.multiprocessing.set_start_method('spawn', force=True)
    # Definir variables de entorno para evitar errores
    os.environ["nnUNet_raw"] = os.getenv("NNUNET_RAW", "/app/modules/Model/nnUNet_raw")
    os.environ["nnUNet_preprocessed"] = os.getenv("NNUNET_PREPROCESSED", "/app/modules/Model/nnUNet_preprocessed")
    os.environ["nnUNet_results"] = os.getenv("NNUNET_RESULTS", "/app/modules/Model/nnUNet_results")

    # Define tus directorios de entrada y salida dentro del contenedor
    unidad = 'cuda'
    input_dir = r"/app/IN"
    output_dir = r"/app/OUT"
    trained_model_dir = r"/app/modules/Model/nnUNet_results/nnUNetTrainer_CE_DC_CLDC__nnUNetResEncUNetMPlans__3d_lowres"

    delete_folder_contents(input_dir)
    delete_folder_contents(output_dir)

    #Image processing

    processor = DICOMProcessor(folder_path, input_dir)
    processor.process()

    print(f"Imagen procesada. Archivo final: {processor.nifti_path}")
    
    # Configura el predictor
    predictor = nnUNetPredictor(
        tile_step_size=0.8,
        use_gaussian=True,
        use_mirroring=False,
        perform_everything_on_device=True,  # Cambia a 'True' si tienes GPU
        device=torch.device(unidad),  # Cambia a 'cuda' si tienes GPU disponible
        verbose=False,
        verbose_preprocessing=False,
        allow_tqdm=True
    )
    
    
    # Inicializa el predictor usando el checkpoint parcheado
    predictor.initialize_from_trained_model_folder(
        trained_model_dir,
        use_folds='all',
        checkpoint_name='checkpoint_final.pth'
    )
    
    
    # Realizar la predicción
    predictor.predict_from_files(
        input_dir,
        output_dir,
        save_probabilities=False,
        overwrite=True,
        num_processes_preprocessing=6,
        num_processes_segmentation_export=3,
        folder_with_segs_from_prev_stage=None,
        num_parts=1,
        part_id=0
    )

    result = nib.load(os.path.join(output_dir, 'image.nii.gz'))
    return result
