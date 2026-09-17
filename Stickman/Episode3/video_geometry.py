from Stickman import manim_geometry as geo
from manim import *
import numpy as np
import math


# ----- Scene Constants ------- #

FRAME_W = 14.22
FRAME_H = 8
GROUND_Y = -2.7

TREE_X = 3.1
TREE_BOTTOM = GROUND_Y
TREE_TOP = 2.65

BRANCH_POINT = np.array([2.75, 0.85, 0])
CLIMB_BRANCH_END = np.array([4.8, 1.65, 0])

LADDER_X = -3.8
LADDER_BOTTOM = GROUND_Y
LADDER_TOP = 1.4


# ----- Coordinate Utilities ------- #

def P(x, y, z=0):
    return np.array([x, y, z], dtype=float)


def xy(point):
    return P(point[0], point[1])


def interpolate(a, b, t):
    return a + (b - a) * t


def quadratic_bezier(a, b, c, t):
    return (1 - t) ** 2 * a + 2 * (1 - t) * t * b + t ** 2 * c


def cubic_bezier(a, b, c, d, t):
    return (
        (1 - t) ** 3 * a
        + 3 * (1 - t) ** 2 * t * b
        + 3 * (1 - t) * t ** 2 * c
        + t ** 3 * d
    )


def polar_point(center, radius, angle):
    return center + P(
        radius * math.cos(angle),
        radius * math.sin(angle)
    )


# ----- Camera Targets ------- #

def wide_camera_target():
    return P(0, 0)


def tree_camera_target():
    return P(2.0, 0.3)


def branch_camera_target():
    return P(3.2, 1.3)


def fall_camera_target():
    return P(1.8, -0.4)


def ladder_camera_target():
    return P(-2.7, -0.2)


def ending_camera_target():
    return P(0, -0.5)


def camera_targets():
    return {
        "wide": wide_camera_target(),
        "tree": tree_camera_target(),
        "branch": branch_camera_target(),
        "fall": fall_camera_target(),
        "ladder": ladder_camera_target(),
        "ending": ending_camera_target(),
    }


# ----- Environment ------- #

def ground_surface():
    return geo.rectangle(
        FRAME_W + 2,
        2.2,
        center=P(0, GROUND_Y - 1.1),
        fill_color="#496B3C",
        fill_opacity=1,
        stroke_width=0
    )


def ground_horizon():
    return Line(
        P(-FRAME_W / 2, GROUND_Y),
        P(FRAME_W / 2, GROUND_Y),
        color="#304C2D",
        stroke_width=4
    )


def grass_blade(x, y, height=0.18, lean=0.04):
    return VGroup(
        Line(P(x, y), P(x - lean, y + height), stroke_width=1.4),
        Line(P(x, y), P(x + lean, y + height * 0.8), stroke_width=1.4)
    ).set_color("#7EAA52")


def ground_grass():
    grass = VGroup()

    for x in np.arange(-7, 7.2, 0.38):
        grass.add(grass_blade(x, GROUND_Y, 0.12 + abs(math.sin(x)) * 0.08))

    return grass


def background_tree(x, y, scale=1):
    trunk = geo.rectangle(
        0.22 * scale,
        1.4 * scale,
        center=P(x, y + 0.7 * scale),
        fill_color="#62452F",
        fill_opacity=1,
        stroke_width=0
    )

    leaves = VGroup(
        Circle(radius=0.55 * scale, color="#477343", fill_opacity=1),
        Circle(radius=0.65 * scale, color="#527E47", fill_opacity=1),
        Circle(radius=0.5 * scale, color="#3D663C", fill_opacity=1)
    )

    leaves.arrange(RIGHT, buff=-0.45 * scale)
    leaves.move_to(P(x, y + 1.55 * scale))

    return VGroup(trunk, leaves)


def background_forest():
    trees = VGroup()

    for x, scale in [
        (-6.2, 1.1),
        (-4.8, 0.8),
        (-2.7, 1.0),
        (5.5, 0.9),
        (6.5, 1.2)
    ]:
        trees.add(background_tree(x, GROUND_Y, scale))

    return trees


def distant_hills():
    return VGroup(
        Polygon(
            P(-7, GROUND_Y),
            P(-5.2, -1.5),
            P(-3.4, -2.0),
            P(-1.1, -1.3),
            P(1.0, -1.9),
            P(3.5, -1.4),
            P(5.4, -2.0),
            P(7, -1.5),
            P(7, GROUND_Y),
            fill_color="#78966A",
            fill_opacity=1,
            stroke_width=0
        )
    )


def sky_background():
    return Rectangle(
        width=FRAME_W + 2,
        height=FRAME_H + 2,
        fill_color="#A9D7E8",
        fill_opacity=1,
        stroke_width=0
    ).move_to(P(0, 0))


def complete_background():
    return VGroup(
        sky_background(),
        distant_hills(),
        background_forest(),
        ground_surface(),
        ground_horizon(),
        ground_grass()
    )


# ----- Main Tree ------- #

def tree_trunk_points():
    return [
        P(2.15, GROUND_Y),
        P(2.45, -0.8),
        P(2.35, 0.5),
        P(2.6, 1.7),
        P(3.0, 2.35),
        P(3.35, 2.1),
        P(3.25, 1.1),
        P(3.55, 0.1),
        P(3.75, GROUND_Y)
    ]


def main_tree_trunk():
    return Polygon(
        *tree_trunk_points(),
        fill_color="#795033",
        fill_opacity=1,
        stroke_color="#4D3425",
        stroke_width=3
    )


def trunk_highlights():
    return VGroup(
        Line(P(2.65, -2.5), P(2.85, 1.9), color="#A8794C", stroke_width=5),
        Line(P(3.15, -2.3), P(3.05, 0.7), color="#5B3D29", stroke_width=3)
    )


def trunk_bark_cracks():
    cracks = VGroup()

    for a, b in [
        ((2.45, -1.9), (2.7, -1.4)),
        ((3.2, -1.2), (3.05, -0.7)),
        ((2.55, 0.1), (2.85, 0.4)),
        ((3.0, 1.2), (3.2, 1.45))
    ]:
        cracks.add(Line(P(*a), P(*b), color="#422D20", stroke_width=2))

    return cracks


def main_branch():
    return geo.cubic_bezier(
        P(2.8, 1.35),
        P(3.3, 1.8),
        P(4.0, 1.4),
        P(5.0, 1.75),
        color="#65452D",
        stroke_width=13
    )


def primary_branches():
    return VGroup(
        Line(P(2.9, 1.7), P(1.8, 2.8), color="#65452D", stroke_width=10),
        Line(P(3.05, 2.0), P(4.0, 2.9), color="#65452D", stroke_width=10),
        Line(P(3.1, 1.6), P(4.6, 2.55), color="#65452D", stroke_width=8)
    )


def secondary_branches():
    return VGroup(
        Line(P(1.9, 2.7), P(1.2, 3.1), color="#65452D", stroke_width=6),
        Line(P(3.9, 2.85), P(4.7, 3.2), color="#65452D", stroke_width=6),
        Line(P(4.4, 2.5), P(5.1, 2.8), color="#65452D", stroke_width=5)
    )


def climbable_branch():
    return geo.cubic_bezier(
        P(2.75, 1.3),
        P(3.35, 1.15),
        P(4.15, 1.4),
        P(5.0, 1.7),
        color="#765035",
        stroke_width=15
    )


def climbable_branch_highlight():
    return geo.cubic_bezier(
        P(2.85, 1.42),
        P(3.4, 1.3),
        P(4.1, 1.55),
        P(4.9, 1.82),
        color="#A8784C",
        stroke_width=3
    )


def branch_texture():
    return VGroup(
        Line(P(3.5, 1.32), P(3.65, 1.52), color="#4D3425", stroke_width=2),
        Line(P(4.0, 1.42), P(4.1, 1.65), color="#4D3425", stroke_width=2),
        Line(P(4.45, 1.57), P(4.55, 1.78), color="#4D3425", stroke_width=2)
    )


def foliage_blob(center, radius, color="#3F733E"):
    offsets = [
        (-0.5, 0.0),
        (0.0, 0.2),
        (0.5, 0.0),
        (-0.25, 0.35),
        (0.3, 0.4)
    ]

    return VGroup(*[
        Circle(
            radius=radius * (0.8 + i % 3 * 0.1),
            fill_color=color,
            fill_opacity=1,
            stroke_color="#315B32",
            stroke_width=2
        ).move_to(center + P(dx * radius, dy * radius))
        for i, (dx, dy) in enumerate(offsets)
    ])


def main_tree_foliage():
    return VGroup(
        foliage_blob(P(2.0, 2.8), 0.8),
        foliage_blob(P(3.1, 3.0), 0.85, "#477D40"),
        foliage_blob(P(4.2, 2.9), 0.85),
        foliage_blob(P(4.8, 2.45), 0.7, "#477D40"),
        foliage_blob(P(1.3, 2.5), 0.65, "#477D40")
    )


def tree_highlight_leaves():
    return VGroup(
        Circle(radius=0.12, fill_color="#8FB95A", fill_opacity=1, stroke_width=0)
        .move_to(P(1.8, 3.25)),
        Circle(radius=0.1, fill_color="#8FB95A", fill_opacity=1, stroke_width=0)
        .move_to(P(3.4, 3.5)),
        Circle(radius=0.12, fill_color="#8FB95A", fill_opacity=1, stroke_width=0)
        .move_to(P(4.5, 3.1))
    )


def complete_main_tree():
    return VGroup(
        main_tree_trunk(),
        trunk_highlights(),
        trunk_bark_cracks(),
        primary_branches(),
        secondary_branches(),
        main_branch(),
        climbable_branch(),
        climbable_branch_highlight(),
        branch_texture(),
        main_tree_foliage(),
        tree_highlight_leaves()
    )


# ----- Stickman Poses ------- #

def climbing_body_position(x, y):
    return P(x, y)


def climbing_head_position(body):
    return body + P(0, 0.48)


def climbing_hand_targets(body):
    return body + P(0.35, 0.25), body + P(-0.25, 0.4)


def climbing_foot_targets(body):
    return body + P(0.3, -0.55), body + P(-0.25, -0.55)


def climbing_pose_data(body):
    left_hand, right_hand = climbing_hand_targets(body)
    left_foot, right_foot = climbing_foot_targets(body)

    return {
        "body": body,
        "head": climbing_head_position(body),
        "hands": (left_hand, right_hand),
        "feet": (left_foot, right_foot)
    }


def first_failure_position():
    return P(2.0, -0.4)


def second_failure_position():
    return P(2.45, 0.15)


def serious_climb_position():
    return P(3.25, 0.9)


def first_failure_hands():
    return climbing_hand_targets(first_failure_position())


def first_failure_feet():
    return climbing_foot_targets(first_failure_position())


def second_failure_hands():
    return climbing_hand_targets(second_failure_position())


def second_failure_feet():
    return climbing_foot_targets(second_failure_position())


def serious_climb_targets():
    return climbing_pose_data(serious_climb_position())


# ----- Branch Breaking ------- #

def branch_break_point():
    return P(3.75, 1.45)


def branch_crack_lines():
    point = branch_break_point()

    return VGroup(
        Line(point + P(-0.13, 0.16), point + P(0.05, -0.08), color="#302019", stroke_width=3),
        Line(point + P(0.05, -0.08), point + P(0.2, 0.12), color="#302019", stroke_width=3),
        Line(point + P(-0.05, 0.1), point + P(0.16, 0.25), color="#302019", stroke_width=2)
    )


def bent_climbable_branch():
    return geo.quadratic_bezier(
        P(2.75, 1.3),
        P(3.45, 1.0),
        P(4.0, 1.15),
        color="#765035",
        stroke_width=13
    )


def broken_branch_piece():
    return geo.cubic_bezier(
        P(3.75, 1.45),
        P(4.0, 1.8),
        P(4.55, 1.35),
        P(5.0, 1.7),
        color="#765035",
        stroke_width=12
    )


def falling_branch_piece():
    branch = broken_branch_piece()
    branch.rotate(-PI / 3, about_point=branch_break_point())
    return branch


def branch_fall_path():
    points = [
        P(3.8, 1.45),
        P(4.2, 0.9),
        P(4.6, 0.2),
        P(4.4, -0.8),
        P(3.8, -1.5)
    ]

    path = VMobject()
    path.set_points_smoothly(points)
    return path


# ----- Falling Effects ------- #

def fall_position(t):
    return cubic_bezier(
        P(3.25, 0.8),
        P(3.9, 0.5),
        P(2.8, -0.5),
        P(2.2, -1.9),
        t
    )


def fall_rotation(t):
    return -2.5 * PI * t


def fall_positions(samples=20):
    return [fall_position(i / (samples - 1)) for i in range(samples)]


def impact_position():
    return P(2.2, -1.9)


def impact_ring_geometry():
    return Circle(
        radius=0.25,
        color="#D6B47A",
        stroke_width=4
    ).move_to(impact_position())


def impact_rays():
    center = impact_position()
    rays = VGroup()

    for angle in np.linspace(0, TAU, 12, endpoint=False):
        rays.add(
            Line(
                center + P(0.25 * math.cos(angle), 0.25 * math.sin(angle)),
                center + P(0.45 * math.cos(angle), 0.45 * math.sin(angle)),
                color="#D6B47A",
                stroke_width=3
            )
        )

    return rays


def dust_particles():
    center = impact_position()
    particles = VGroup()

    for angle in np.linspace(0, TAU, 10, endpoint=False):
        particles.add(
            Dot(
                center + P(
                    0.5 * math.cos(angle),
                    0.25 + 0.35 * math.sin(angle)
                ),
                radius=0.045,
                color="#C5A77A"
            )
        )

    return particles


def complete_impact_effect():
    return VGroup(
        impact_ring_geometry(),
        impact_rays(),
        dust_particles()
    )


# ----- Ladder ------- #

def ladder_left_bottom():
    return P(LADDER_X, LADDER_BOTTOM)


def ladder_right_bottom():
    return P(LADDER_X + 0.8, LADDER_BOTTOM)


def ladder_left_top():
    return P(LADDER_X + 0.2, LADDER_TOP)


def ladder_right_top():
    return P(LADDER_X + 1.0, LADDER_TOP)


def ladder_rails():
    return VGroup(
        Line(ladder_left_bottom(), ladder_left_top(), color="#8B5E3C", stroke_width=9),
        Line(ladder_right_bottom(), ladder_right_top(), color="#8B5E3C", stroke_width=9)
    )


def ladder_rungs():
    rungs = VGroup()

    for y in np.arange(LADDER_BOTTOM + 0.25, LADDER_TOP, 0.35):
        t = (y - LADDER_BOTTOM) / (LADDER_TOP - LADDER_BOTTOM)
        left = interpolate(ladder_left_bottom(), ladder_left_top(), t)
        right = interpolate(ladder_right_bottom(), ladder_right_top(), t)

        rungs.add(
            Line(left, right, color="#A87548", stroke_width=6)
        )

    return rungs


def ladder_highlights():
    return Line(
        ladder_left_bottom() + P(0.08, 0),
        ladder_left_top() + P(0.08, 0),
        color="#C3915C",
        stroke_width=2
    )


def ladder_shadow():
    return Line(
        ladder_left_bottom() + P(-0.1, -0.05),
        ladder_right_bottom() + P(0.2, -0.05),
        color="#35402D",
        stroke_width=8
    )


def complete_ladder():
    return VGroup(
        ladder_shadow(),
        ladder_rails(),
        ladder_rungs(),
        ladder_highlights()
    )


# ----- Ladder Failure Pose ------- #

def ladder_step_position(step=0):
    y = LADDER_BOTTOM + 0.3 + step * 0.3
    return P(LADDER_X + 0.4, y)


def ladder_body_position(step=0):
    return ladder_step_position(step) + P(0, 0.1)


def ladder_head_position(step=0):
    return ladder_body_position(step) + P(0, 0.48)


def ladder_hand_targets(step=0):
    body = ladder_body_position(step)
    return body + P(-0.25, 0.2), body + P(0.3, 0.3)


def ladder_foot_targets(step=0):
    body = ladder_body_position(step)
    return body + P(-0.2, -0.5), body + P(0.25, -0.5)


def ladder_climbing_data(step=0):
    return {
        "body": ladder_body_position(step),
        "head": ladder_head_position(step),
        "hands": ladder_hand_targets(step),
        "feet": ladder_foot_targets(step)
    }


def ladder_failure_body():
    return P(LADDER_X + 0.4, -1.5)


def ladder_failure_head():
    return ladder_failure_body() + P(0, 0.48)


def ladder_failure_hands():
    body = ladder_failure_body()
    return body + P(-0.4, 0.2), body + P(0.4, 0.15)


def ladder_failure_feet():
    body = ladder_failure_body()
    return body + P(-0.25, -0.5), body + P(0.3, -0.5)


def ladder_failure_data():
    return {
        "body": ladder_failure_body(),
        "head": ladder_failure_head(),
        "hands": ladder_failure_hands(),
        "feet": ladder_failure_feet()
    }


# ----- Ending Pose ------- #

def final_body_position():
    return P(-1.0, -1.65)


def final_head_position():
    return final_body_position() + P(0, 0.5)


def final_hands():
    body = final_body_position()
    return body + P(-0.35, 0.1), body + P(0.35, 0.1)


def final_feet():
    body = final_body_position()
    return body + P(-0.2, -0.5), body + P(0.2, -0.5)


def crying_pose_data():
    return {
        "body": final_body_position(),
        "head": final_head_position(),
        "hands": final_hands(),
        "feet": final_feet()
    }


def ending_text_position():
    return P(0, 1.2)


def ending_subtitle_position():
    return P(0, 0.65)


def ending_composition():
    title = Text(
        "THE END",
        font_size=0.85,
        weight=BOLD,
        color=WHITE
    ).move_to(ending_text_position())

    subtitle = Text(
        "Sometimes even the ladder fails you.",
        font_size=0.3,
        color="#E6E6E6"
    ).move_to(ending_subtitle_position())

    return VGroup(title, subtitle)


# ----- Complete Geometry Maps ------- #

def scene_one_geometry():
    return {
        "background": complete_background(),
        "tree": complete_main_tree(),
        "camera": wide_camera_target()
    }


def scene_two_geometry():
    return {
        "background": complete_background(),
        "tree": complete_main_tree(),
        "camera": tree_camera_target(),
        "pose": climbing_pose_data(first_failure_position())
    }


def scene_three_geometry():
    return {
        "background": complete_background(),
        "tree": complete_main_tree(),
        "camera": tree_camera_target(),
        "pose": climbing_pose_data(second_failure_position())
    }


def scene_four_geometry():
    return {
        "background": complete_background(),
        "tree": complete_main_tree(),
        "camera": branch_camera_target(),
        "pose": serious_climb_targets()
    }


def scene_five_geometry():
    return {
        "background": complete_background(),
        "tree": complete_main_tree(),
        "broken_branch": broken_branch_piece(),
        "cracks": branch_crack_lines(),
        "fall_path": branch_fall_path(),
        "impact": complete_impact_effect(),
        "camera": fall_camera_target()
    }


def scene_six_geometry():
    return {
        "background": complete_background(),
        "ladder": complete_ladder(),
        "ladder_pose": ladder_climbing_data(3),
        "failure_pose": ladder_failure_data(),
        "ending_pose": crying_pose_data(),
        "ending": ending_composition(),
        "camera": ending_camera_target()
    }


def complete_episode_geometry():
    return {
        "constants": {
            "ground_y": GROUND_Y,
            "tree_x": TREE_X,
            "ladder_x": LADDER_X
        },
        "camera_targets": camera_targets(),
        "scenes": {
            1: scene_one_geometry(),
            2: scene_two_geometry(),
            3: scene_three_geometry(),
            4: scene_four_geometry(),
            5: scene_five_geometry(),
            6: scene_six_geometry()
        }
}
