"""Lightweight Rerun visualizer for 2D Pure Pursuit simulations.

Provides 2D spatial rendering (target, missile, line-of-sight, trajectory trails)
and real-time telemetry charts (closing distance, heading, velocities).
Supports both native GUI and browser-based Web viewer (ideal for WSL).
"""

import math
from typing import Any, Dict, List, Optional

try:
    import rerun as rr

    RERUN_AVAILABLE = True
except ImportError:
    RERUN_AVAILABLE = False


class SimVisualizer:
    def __init__(
        self,
        exp_name: str,
        web: bool = False,
        enabled: bool = True,
        save_path: Optional[str] = None,
    ):
        """Initialize Rerun recording session.

        Args:
            exp_name: Name of the experiment shown in Rerun UI.
            web: If True, serve the web viewer (recommended for WSL/Windows).
            enabled: If False, disables visualization entirely.
            save_path: Optional path to save recording as a .rrd file.
        """
        self.enabled = enabled and RERUN_AVAILABLE
        self.web = web

        if not self.enabled:
            if enabled and not RERUN_AVAILABLE:
                print("\n[Notice] 'rerun-sdk' is not installed.")
                print("Run: pip install rerun-sdk (or activate your venv) to enable live 2D telemetry visualization.\n")
            return

        self.missile_trail: List[List[float]] = []
        self.target_trail: List[List[float]] = []

        if save_path:
            rr.init(exp_name, spawn=False)
            rr.save(save_path)
            print(f"[Rerun] Saving recording to {save_path}")
        elif web:
            rr.init(exp_name, spawn=False)
            server_uri = rr.serve_grpc()
            rr.serve_web_viewer(connect_to=server_uri, open_browser=True)
            print("\n🌐 [Rerun] Web viewer live at: http://localhost:9090 (open in your Windows browser)")
        else:
            try:
                rr.init(exp_name, spawn=True)
            except Exception as e:
                print(f"[Rerun] Native GUI window failed ({e}), falling back to web viewer...")
                self.web = True
                rr.init(exp_name, spawn=False)
                server_uri = rr.serve_grpc()
                rr.serve_web_viewer(connect_to=server_uri, open_browser=True)
                print("\n🌐 [Rerun] Web viewer live at: http://localhost:9090 (open in your Windows browser)")

    def log_step(
        self,
        t: float,
        missile: Any,
        target: Any,
        distance: float,
        hit: bool = False,
        extra_telemetry: Optional[Dict[str, float]] = None,
    ):
        """Log a simulation step to Rerun timeline."""
        if not self.enabled:
            return

        rr.set_time("sim_time", duration=t)

        # Record trails
        self.missile_trail.append([missile.x, missile.y])
        self.target_trail.append([target.x, target.y])

        # 1. 2D Spatial Entities
        # Target (Red)
        rr.log(
            "world/target",
            rr.Points2D([[target.x, target.y]], colors=[[255, 60, 60]], radii=[6]),
        )
        # Interceptor Missile (Blue)
        rr.log(
            "world/missile",
            rr.Points2D([[missile.x, missile.y]], colors=[[50, 150, 255]], radii=[5]),
        )

        # Line of Sight (LOS) vector line
        rr.log(
            "world/los",
            rr.LineStrips2D(
                [[[missile.x, missile.y], [target.x, target.y]]],
                colors=[[180, 180, 180]],
            ),
        )

        # Trajectory Trails
        rr.log(
            "world/target_trail",
            rr.LineStrips2D([self.target_trail], colors=[[255, 140, 140]]),
        )
        rr.log(
            "world/missile_trail",
            rr.LineStrips2D([self.missile_trail], colors=[[120, 180, 255]]),
        )

        # Missile Heading Vector Arrow
        heading = getattr(missile, "heading_deg", None)
        if heading is None:
            # If ideal pursuit, heading is along LOS
            heading = math.atan2(target.y - missile.y, target.x - missile.x)
        arrow_len = 30.0
        rr.log(
            "world/missile_heading",
            rr.Arrows2D(
                origins=[[missile.x, missile.y]],
                vectors=[[math.cos(heading) * arrow_len, math.sin(heading) * arrow_len]],
                colors=[[0, 220, 255]],
            ),
        )

        # 2. Telemetry Time-Series Plots
        rr.log("telemetry/distance", rr.Scalars(distance))
        if extra_telemetry:
            for name, val in extra_telemetry.items():
                rr.log(f"telemetry/{name}", rr.Scalars(val))

        # 3. Intercept Event
        if hit:
            rr.log(
                "world/intercept_marker",
                rr.Points2D([[missile.x, missile.y]], colors=[[255, 215, 0]], radii=[15]),
            )
            rr.log("events", rr.TextLog(f"Target intercepted at t={t:.2f}s! Distance: {distance:.2f}m"))

    def finish(self):
        """Finalize simulation logging and keep web viewer alive if active."""
        if not self.enabled:
            return
        if self.web:
            print("\n🌐 [Rerun] Simulation complete. Interactive viewer running at: http://localhost:9090")
            print("Press Enter or Ctrl+C to close viewer...")
            try:
                input()
            except (KeyboardInterrupt, EOFError):
                pass
