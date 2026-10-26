import os
import shutil
import pydicom

# ============================================================
# 1. FOLDERS
# ============================================================

input_folder = input("Input folder: ")
output_folder = input("Output folder: ")

os.makedirs(output_folder, exist_ok=True)


# ============================================================
# 2. READ ALL DICOM FILES, GROUPED BY SEQUENCE
# ============================================================

dicoms = {}

for filename in os.listdir(input_folder):
    filepath = os.path.join(input_folder, filename)

    try:
        dcm = pydicom.dcmread(filepath)

        # A series is one sequence, for example SA Cine or 4CH Cine.
        series = dcm.SeriesInstanceUID

        if series not in dicoms:
            dicoms[series] = []

        dicoms[series].append((dcm, filename))

    except:
        # Ignore anything that is not a readable DICOM
        pass


# ============================================================
# 3. REORDER ONLY MULTI-SLICE CINE SEQUENCES
# ============================================================

for series, images in dicoms.items():

    try:
        # A multi-slice cine has more than one slice location and more than
        # one trigger time. A non-cine stack has only one trigger time (or no
        # TriggerTime tag at all).
        slice_locations = set(float(dcm.SliceLocation) for dcm, filename in images)
        trigger_times = set(float(dcm.TriggerTime) for dcm, filename in images)

        is_multislice_cine = len(slice_locations) > 1 and len(trigger_times) > 1

    except:
        is_multislice_cine = False

    if is_multislice_cine:
        # First sort by slice. Within each slice, sort by cardiac phase.
        images.sort(key=lambda x: (float(x[0].SliceLocation), float(x[0].TriggerTime)))

        for number, (dcm, filename) in enumerate(images, start=1):
            dcm.InstanceNumber = number
            dcm.save_as(os.path.join(output_folder, filename))

        print("Reordered:", images[0][0].SeriesDescription)

    else:
        # Keep all other sequences exactly as they were.
        for dcm, filename in images:
            shutil.copy2(
                os.path.join(input_folder, filename),
                os.path.join(output_folder, filename),
            )


# ============================================================
# 4. DONE
# ============================================================

print("Done.")
print("Output folder:", output_folder)
