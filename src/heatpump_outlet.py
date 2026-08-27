"""
Air Conditioner Hose-to-Door Adapter Generator
----------------------------------------------
Generates a 3D point cloud model transitioning a circular air conditioning hose 
interface to a rectangular door/window vent adapter, then reconstructs a 3D 
mesh (STL) using Poisson surface reconstruction via Open3D.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation
import open3d as o3d

# ==========================================
# CONFIGURATION & GEOMETRY PARAMETERS
# ==========================================

# Resolution settings
DEFINITION = 500  # Angular/per-layer point resolution
DEFINITION_DEPTH = 100  # Number of depth layers

# Hose interface dimensions (mm)
HOSE_INNER_RADIUS = 74.0
HOSE_OUTER_RADIUS = 77.0
HOSE_DEPTH = 50.0

# Door outlet interface dimensions (mm)
DOOR_INNER_HEIGHT = 95.0
DOOR_OUTER_HEIGHT = DOOR_INNER_HEIGHT + 5.0
DOOR_INNER_WIDTH = 130.0
DOOR_OUTER_WIDTH = DOOR_INNER_WIDTH + 5.0

# Transition geometry settings
TRANSITION_WIDTH = 50.0

# Positional offsets & orientation
Y_SHIFT = 0.0
Z_SHIFT = -47.5
HOSE_ROTATE_ANGLE = 0.0  # Rotation in radians


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def linear_interp(step_i: int, max_steps: int, x1: float, x2: float) -> float:
    """Linearly interpolates between two scalar values across step increments."""
    step = (x2 - x1) / max_steps
    return x1 + step * float(step_i)


def plot_3d(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> None:
    """Utility function to display 3D scatter plots for geometry debugging."""
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.scatter(x, y, z, s=1)
    ax.axis('auto')
    plt.show()


# ==========================================
# GEOMETRY GENERATION
# ==========================================

def generate_hose(def_count: int, def_depth: int, hose_depth: float):
    """Generates inner and outer cylindrical point clouds for the hose end."""
    depth_step = hose_depth / def_depth
    angle_step = 360.0 / def_count

    hose_inner = np.zeros((def_count * def_depth, 3))
    hose_outer = np.zeros((def_count * def_depth, 3))

    for j in range(def_depth):
        for i in range(def_count):
            idx = i + j * def_count
            rad = np.radians(i * angle_step)

            # X-axis represents axial depth
            hose_inner[idx, 0] = -depth_step * j
            hose_outer[idx, 0] = -depth_step * j

            # Y and Z represent circular cross-section
            hose_inner[idx, 1] = HOSE_INNER_RADIUS * np.cos(rad) + Y_SHIFT
            hose_outer[idx, 1] = HOSE_OUTER_RADIUS * np.cos(rad) + Y_SHIFT

            hose_inner[idx, 2] = HOSE_INNER_RADIUS * np.sin(rad) + Z_SHIFT
            hose_outer[idx, 2] = HOSE_OUTER_RADIUS * np.sin(rad) + Z_SHIFT

    return hose_inner, hose_outer, depth_step


def generate_screw_thread(revs: int = 5, max_i: int = 6, max_j: int = 5000) -> np.ndarray:
    """Generates point cloud geometry for the internal hose screw threads."""
    angle_step_i = 360.0 / max_i
    angle_step_j = (revs * 360.0) / max_j
    spiral_screw = np.zeros((max_i, max_j, 3))

    a = 2.0
    h = 1.0
    denominator = np.sqrt(HOSE_INNER_RADIUS ** 2 + h ** 2)

    for j in range(max_j):
        for i in range(max_i):
            u = np.radians(i * angle_step_i)
            t = np.radians(j * angle_step_j)

            spiral_screw[i, j, 0] = h * t + HOSE_INNER_RADIUS * a * np.sin(u) / denominator - 30.0
            spiral_screw[i, j, 1] = (HOSE_INNER_RADIUS * np.cos(t) - a * np.cos(u) * np.cos(t) + 
                                     h * a * np.sin(t) * np.sin(u) / denominator + Y_SHIFT)
            spiral_screw[i, j, 2] = (HOSE_INNER_RADIUS * np.sin(t) - a * np.cos(u) * np.sin(t) - 
                                     h * a * np.cos(t) * np.sin(u) / denominator + Z_SHIFT)

    return spiral_screw.reshape(-1, 3)


def generate_door_sections(pointy: int, pointz: int, depth_step: float):
    """Generates point clouds for horizontal and side faces of the rectangular door outlet."""
    door_inner_width_step = DOOR_INNER_WIDTH / pointy
    door_outer_width_step = DOOR_OUTER_WIDTH / pointy
    door_inner_height_step = DOOR_INNER_HEIGHT / pointz
    door_outer_height_step = DOOR_OUTER_HEIGHT / pointz

    door_inner_horiz = np.zeros((pointy * DEFINITION_DEPTH, 2, 3))
    door_outer_horiz = np.zeros((pointy * DEFINITION_DEPTH, 2, 3))
    door_inner_side = np.zeros((pointz * DEFINITION_DEPTH, 2, 3))
    door_outer_side = np.zeros((pointz * DEFINITION_DEPTH, 2, 3))

    # Horizontal Top/Bottom Section Calculations
    for j in range(DEFINITION_DEPTH):
        for i in range(pointy):
            idx = i + j * pointy
            x_val = depth_step * j + TRANSITION_WIDTH

            # Bottom horizontal edge
            door_inner_horiz[idx, 0] = [x_val, -DOOR_INNER_WIDTH * 0.5 + i * door_inner_width_step, -DOOR_INNER_HEIGHT]
            door_outer_horiz[idx, 0] = [x_val, -DOOR_OUTER_WIDTH * 0.5 + i * door_outer_width_step, -DOOR_OUTER_HEIGHT]

            # Top horizontal edge
            door_inner_horiz[idx, 1] = [x_val, -DOOR_INNER_WIDTH * 0.5 + i * door_inner_width_step, -0.5 * (DOOR_OUTER_HEIGHT - DOOR_INNER_HEIGHT)]
            door_outer_horiz[idx, 1] = [x_val, -DOOR_OUTER_WIDTH * 0.5 + i * door_outer_width_step, 0]

    # Vertical Side Sections
    for j in range(DEFINITION_DEPTH):
        for i in range(pointz):
            idx = i + j * pointz
            x_val = depth_step * j + TRANSITION_WIDTH

            # Left side
            door_inner_side[idx, 0] = [x_val, -DOOR_INNER_WIDTH * 0.5 + 0.5 * (DOOR_OUTER_WIDTH - DOOR_INNER_WIDTH), -DOOR_INNER_HEIGHT + i * door_inner_height_step]
            door_outer_side[idx, 0] = [x_val, -DOOR_OUTER_WIDTH * 0.5, -DOOR_OUTER_HEIGHT + i * door_outer_height_step]

            # Right side
            door_inner_side[idx, 1] = [x_val, -(-DOOR_INNER_WIDTH * 0.5 + 0.5 * (DOOR_OUTER_WIDTH - DOOR_INNER_WIDTH)), -DOOR_INNER_HEIGHT + i * door_inner_height_step]
            door_outer_side[idx, 1] = [x_val, -(-DOOR_OUTER_WIDTH * 0.5), -DOOR_OUTER_HEIGHT + i * door_outer_height_step]

    return door_inner_horiz, door_outer_horiz, door_inner_side, door_outer_side


def generate_transition_points(hose_inner, hose_outer, door_inner_horiz, door_outer_horiz,
                               door_inner_side, door_outer_side, pointy, pointz):
    """Interpolates points between circular hose end and rectangular door end."""
    half_pz = int(0.5 * pointz)
    transition_inner = np.zeros((DEFINITION * DEFINITION_DEPTH, 3))
    transition_outer = np.zeros((DEFINITION * DEFINITION_DEPTH, 3))

    for j in range(DEFINITION_DEPTH):
        # Top and Bottom region interpolation
        for i in range(pointy):
            idx_upper = i + j * DEFINITION
            idx_lower = i + pointy + j * DEFINITION
            
            src_idx_up = pointy + half_pz - i
            src_idx_low = DEFINITION - pointy - half_pz + i

            for dim in range(3):
                transition_inner[idx_upper, dim] = linear_interp(j, DEFINITION_DEPTH, hose_inner[src_idx_up, dim], door_inner_horiz[i, 1, dim])
                transition_outer[idx_upper, dim] = linear_interp(j, DEFINITION_DEPTH, hose_outer[src_idx_up, dim], door_outer_horiz[i, 1, dim])
                transition_inner[idx_lower, dim] = linear_interp(j, DEFINITION_DEPTH, hose_inner[src_idx_low, dim], door_inner_horiz[i, 0, dim])
                transition_outer[idx_lower, dim] = linear_interp(j, DEFINITION_DEPTH, hose_outer[src_idx_low, dim], door_outer_horiz[i, 0, dim])

        # Left and Right side region interpolation
        for i in range(half_pz):
            base_idx = 2 * pointy + j * DEFINITION
            
            # Map index points
            indices = [
                (pointy + pointz - i, i + half_pz, 0, 0),
                (i, i + half_pz, 1, pointz),
                (pointy + pointz + half_pz - i, i, 0, half_pz),
                (DEFINITION - half_pz + i, i, 1, half_pz + pointz)
            ]

            for hose_idx, door_idx_i, side_idx, offset in indices:
                t_idx = i + offset + base_idx
                for dim in range(3):
                    transition_inner[t_idx, dim] = linear_interp(j, DEFINITION_DEPTH, hose_inner[hose_idx, dim], door_inner_side[door_idx_i, side_idx, dim])
                    transition_outer[t_idx, dim] = linear_interp(j, DEFINITION_DEPTH, hose_outer[hose_idx, dim], door_outer_side[door_idx_i, side_idx, dim])

    return transition_inner, transition_outer


# ==========================================
# MAIN EXECUTABLE PIPELINE
# ==========================================

def main():
    # Grid division parameters
    pointy = int(DEFINITION * 0.5 * DOOR_INNER_WIDTH / (DOOR_INNER_HEIGHT + DOOR_INNER_WIDTH))
    pointz = int(0.5 * DEFINITION - pointy)

    print(f"Grid setup: pointy={pointy}, pointz={pointz}")

    # Step 1: Generate Hose and Thread Geometry
    hose_inner, hose_outer, depth_step = generate_hose(DEFINITION, DEFINITION_DEPTH, HOSE_DEPTH)
    screw_thread = generate_screw_thread()

    # Apply rotation vector transformation
    r = Rotation.from_rotvec([0, 0, HOSE_ROTATE_ANGLE])
    screw_thread = r.apply(screw_thread)
    hose_inner = r.apply(hose_inner)
    hose_outer = r.apply(hose_outer)

    # Step 2: Generate Door Geometry
    door_inner_horiz, door_outer_horiz, door_inner_side, door_outer_side = generate_door_sections(pointy, pointz, depth_step)

    # Step 3: Generate Smooth Transition Point Cloud
    transition_inner, transition_outer = generate_transition_points(
        hose_inner, hose_outer, door_inner_horiz, door_outer_horiz, 
        door_inner_side, door_outer_side, pointy, pointz
    )

    # Step 4: Combine Point Cloud Assemblies
    completeshape_outer = np.concatenate((
        hose_outer,
        door_outer_horiz[:, 0, :], door_outer_horiz[:, 1, :],
        door_outer_side[:, 0, :], door_outer_side[:, 1, :],
        transition_outer
    ), axis=0)

    completeshape_inner = np.concatenate((
        hose_inner,
        door_inner_horiz[:, 0, :], door_inner_horiz[:, 1, :],
        door_inner_side[:, 0, :], door_inner_side[:, 1, :],
        transition_inner
    ), axis=0)

    # Step 5: Process Outer Point Cloud & Normals
    pcd_outer = o3d.geometry.PointCloud()
    pcd_outer.points = o3d.utility.Vector3dVector(completeshape_outer)
    pcd_outer.estimate_normals()
    pcd_outer.orient_normals_consistent_tangent_plane(10)

    # Step 6: Process Inner Point Cloud & Invert Normals (facing inwards)
    pcd_inner = o3d.geometry.PointCloud()
    pcd_inner.points = o3d.utility.Vector3dVector(completeshape_inner)
    pcd_inner.estimate_normals()
    pcd_inner.orient_normals_consistent_tangent_plane(10)
    
    # Invert inner normals so mesh faces point inward
    inner_normals = np.asarray(pcd_inner.normals) * -1
    pcd_inner.normals = o3d.utility.Vector3dVector(inner_normals)

    # Combine inner & outer shells
    pcd_combined = pcd_outer + pcd_inner

    # Step 7: Mesh Reconstruction using Poisson Algorithm
    print("Reconstructing 3D mesh surface via Poisson method...")
    with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug):
        mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd_combined, depth=9)

    mesh.compute_vertex_normals()
    mesh.paint_uniform_color([0.5, 0.5, 0.5])  # Paint gray for clean shading view

    # Step 8: Visualization and Export
    output_filename = "airconditioningadaptor.stl"
    o3d.io.write_triangle_mesh(output_filename, mesh)
    print(f"Mesh successfully generated and saved to {output_filename}")

    o3d.visualization.draw_geometries(
        [mesh],
        zoom=0.664,
        front=[-0.4761, -0.4698, -0.7434],
        lookat=[1.8900, 3.2596, 0.9284],
        up=[0.2304, -0.8825, 0.4101]
    )


if __name__ == "__main__":
    main()