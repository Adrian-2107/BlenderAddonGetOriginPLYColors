# PLY Original Color Restoration – Blender Add-on

This repository contains a Blender add-on for restoring the original vertex colors of imported PLY point clouds.

The add-on automatically creates the required material, Geometry Nodes setup, and modifier, allowing the point cloud to be displayed with its original colors as a point-based visualization.

## Requirements

- Blender 5.0.1

## Installation

1. Download recover_origin_colors.py file.
2. Open Blender.
3. Go to **Edit → Preferences → Add-ons**.
4. Click **Install...**.
5. Select the file `recover_origin_colors.py`.
6. Enable the add-on.

## Usage

The add-on can be accessed directly from the **Object** menu.
<img width="555" height="39" alt="image" src="https://github.com/user-attachments/assets/a3881d29-1b5f-4871-a18e-ef1493358137" />

## Notes

- The original PLY file is **not modified**.
- The add-on only creates and assigns the required material, Geometry Nodes setup, and modifier inside Blender.
- The add-on expects the vertex color attribute to be named **`Col`**.
