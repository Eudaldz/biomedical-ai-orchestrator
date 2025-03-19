import os
import SimpleITK as sitk


class DICOMProcessor:
    """
    Clase para procesar imágenes DICOM:
    - Convierte DICOM a NIfTI (.nii.gz) usando SimpleITK.
    """

    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.nifti_path = os.path.join(self.output_directory, "image_0000.nii.gz")

        # Asegurar que el directorio de salida existe
        os.makedirs(self.output_directory, exist_ok=True)

    def dicom_to_nifti(self):
        """
        Convierte una serie DICOM a un archivo NIfTI usando SimpleITK.
        """
        try:
            # Configurar el lector de series DICOM
            reader = sitk.ImageSeriesReader()
            dicom_names = reader.GetGDCMSeriesFileNames(self.input_directory)
            reader.SetFileNames(dicom_names)

            # Leer la imagen DICOM
            image = reader.Execute()

            # Reorientar la imagen a RAS+
            ras_image = self.reorient_to_ras(image)

            # Guardar la imagen como NIfTI
            sitk.WriteImage(ras_image, self.nifti_path)

        except Exception as e:
            raise RuntimeError(f"Error en la conversión DICOM a NIfTI: {e}")

    def reorient_to_ras(self, image):
        """
        Reorienta una imagen al espacio de coordenadas RAS+.
        """
        # Definir la orientación deseada (RAS+)
        ras_orientation = "RAS"

        # Crear un filtro de reorientación
        orient_filter = sitk.DICOMOrientImageFilter()
        orient_filter.SetDesiredCoordinateOrientation(ras_orientation)

        # Aplicar la reorientación
        ras_image = orient_filter.Execute(image)

        return ras_image


    def process(self):
        """
        Ejecuta el pipeline completo:
        - Convierte DICOM a NIfTI.
        """
        self.dicom_to_nifti()