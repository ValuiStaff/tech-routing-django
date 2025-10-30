import re
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from core.models import Technician, ServiceRequest, Assignment, GoogleMapsConfig
from maps.services import GeocodingService, DistanceService


class RoutingService:
    """Service for OR-Tools based job assignment"""
    
    def __init__(self):
        self.config = GoogleMapsConfig.load()
        self.geocoding_service = GeocodingService()
        self.distance_service = DistanceService()
        self.avg_kph = self.config.avg_speed_kph
    
    def color_for_name(self, name: str) -> str:
        """Generate color for technician"""
        h = hashlib.md5(name.encode("utf-8")).hexdigest()
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        r = int(120 + r / 2)
        g = int(120 + g / 2)
        b = int(120 + b / 2)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def solve(self, technicians: List[Technician], service_requests: List[ServiceRequest],
              assigned_date: datetime) -> Tuple[List[Dict], List[ServiceRequest], float]:
        """
        Solve routing problem using OR-Tools
        Returns: (assignments, unserved_requests, total_travel_time)
        """
        import sys
        print(f"\n{'='*80}")
        print(f"ROUTING SERVICE - SOLVE CALLED")
        print(f"{'='*80}")
        print(f"Technicians provided: {len(technicians)}")
        print(f"Service requests provided: {len(service_requests)}")
        sys.stdout.flush()
        
        # Filter valid technicians and requests
        techs = [t for t in technicians if t.depot_lat is not None and t.depot_lon is not None]
        reqs = [r for r in service_requests if r.lat is not None and r.lon is not None and r.status == 'pending']
        
        print(f"Valid technicians: {len(techs)}")
        print(f"Valid pending requests: {len(reqs)}")
        sys.stdout.flush()
        
        if not techs:
            raise ValueError("No technicians with valid depot coordinates.")
        if not reqs:
            return [], [], 0.0
        
        K = len(techs)
        I = len(reqs)
        
        # Build travel time matrices with timing
        import time
        import math
        
        print(f"\nBuilding distance matrices...")
        start_time = time.time()
        
        t_s_i = {}  # Tech depot to customer
        t_i_j = {}  # Customer to customer
        t_i_e = {}  # Customer to depot
        
        # Calculate matrices (using fast Haversine - no API calls)
        matrix_calc_start = time.time()
        
        for k in range(K):
            for i in range(I):
                travel_time = self.distance_service.travel_minutes(
                    techs[k].depot_lat, techs[k].depot_lon,
                    reqs[i].lat, reqs[i].lon,
                    self.avg_kph
                )
                # Check for valid values
                if travel_time is None or math.isnan(travel_time) or travel_time < 0:
                    print(f"Invalid travel time for tech {k} to request {i}: {travel_time}")
                    travel_time = 999999  # Use a large penalty for invalid routes
                t_s_i[(k, i)] = travel_time
                
                travel_time_e = self.distance_service.travel_minutes(
                    reqs[i].lat, reqs[i].lon,
                    techs[k].depot_lat, techs[k].depot_lon,
                    self.avg_kph
                )
                if travel_time_e is None or math.isnan(travel_time_e) or travel_time_e < 0:
                    print(f"Invalid travel time from request {i} to tech {k}: {travel_time_e}")
                    travel_time_e = 999999
                t_i_e[(k, i)] = travel_time_e
        
        for i in range(I):
            for j in range(I):
                if i == j:
                    t_i_j[(i, j)] = 0.0
                else:
                    travel_time = self.distance_service.travel_minutes(
                        reqs[i].lat, reqs[i].lon,
                        reqs[j].lat, reqs[j].lon,
                        self.avg_kph
                    )
                    if travel_time is None or math.isnan(travel_time) or travel_time < 0:
                        print(f"Invalid travel time from request {i} to request {j}: {travel_time}")
                        travel_time = 999999
                    t_i_j[(i, j)] = travel_time
        
        matrix_time = time.time() - matrix_calc_start
        print(f"✓ Distance matrix built in {matrix_time:.2f} seconds ({K*I*2 + I*I} calculations)")
        
        # DEBUG: Show sample travel times and distances
        print(f"\n{'='*80}")
        print(f"TRAVEL TIME ANALYSIS")
        print(f"{'='*80}")
        print(f"Average speed: {self.avg_kph} km/h")
        print(f"\nSample distances and times:")
        
        # Show a few sample calculations
        if K > 0 and I > 0:
            # Tech 0 to first request
            sample_dist_km = DistanceService.haversine_km(
                techs[0].depot_lat, techs[0].depot_lon,
                reqs[0].lat, reqs[0].lon
            )
            sample_time = t_s_i.get((0, 0), 0)
            print(f"  Tech '{techs[0].user.username}' depot → Request '{reqs[0].name}':")
            print(f"    Distance: {sample_dist_km:.2f} km")
            print(f"    Travel time: {sample_time:.2f} minutes ({sample_time/60:.2f} hours)")
            print(f"    Speed used: {self.avg_kph} km/h")
            
            # Between two requests if available
            if I > 1:
                sample_dist_km2 = DistanceService.haversine_km(
                    reqs[0].lat, reqs[0].lon,
                    reqs[1].lat, reqs[1].lon
                )
                sample_time2 = t_i_j.get((0, 1), 0)
                print(f"  Request '{reqs[0].name}' → Request '{reqs[1].name}':")
                print(f"    Distance: {sample_dist_km2:.2f} km")
                print(f"    Travel time: {sample_time2:.2f} minutes ({sample_time2/60:.2f} hours)")
        
        # Show max and min travel times
        all_times = list(t_s_i.values()) + list(t_i_j.values()) + list(t_i_e.values())
        valid_times = [t for t in all_times if t < 999999 and t > 0]
        
        if valid_times:
            min_time = min(valid_times)
            max_time = max(valid_times)
            avg_time = sum(valid_times) / len(valid_times)
            
            print(f"\nTravel time statistics:")
            print(f"  Min travel time: {min_time:.2f} minutes ({min_time/60:.2f} hours)")
            print(f"  Max travel time: {max_time:.2f} minutes ({max_time/60:.2f} hours)")
            print(f"  Average travel time: {avg_time:.2f} minutes ({avg_time/60:.2f} hours)")
            
            # Analyze if times are high
            print(f"\n⚠️  TRAVEL TIME ANALYSIS:")
            if max_time > 60:  # More than 1 hour
                print(f"  ⚠️  WARNING: Some locations are {max_time/60:.1f} hours apart!")
                print(f"  This suggests locations are far from each other or speed setting is too low.")
                
                # Find which pairs have high travel times
                high_time_pairs = []
                for (k, i), time_val in t_s_i.items():
                    if time_val > 60:
                        dist = DistanceService.haversine_km(
                            techs[k].depot_lat, techs[k].depot_lon,
                            reqs[i].lat, reqs[i].lon
                        )
                        high_time_pairs.append((
                            f"Tech '{techs[k].user.username}' → '{reqs[i].name}'",
                            dist, time_val
                        ))
                
                for (i, j), time_val in t_i_j.items():
                    if time_val > 60:
                        dist = DistanceService.haversine_km(
                            reqs[i].lat, reqs[i].lon,
                            reqs[j].lat, reqs[j].lon
                        )
                        high_time_pairs.append((
                            f"'{reqs[i].name}' → '{reqs[j].name}'",
                            dist, time_val
                        ))
                
                if high_time_pairs:
                    print(f"\n  Long travel time pairs (>1 hour):")
                    for pair_name, dist_km, time_min in high_time_pairs[:10]:  # Show first 10
                        print(f"    - {pair_name}: {dist_km:.2f} km = {time_min:.1f} min")
                
                print(f"\n  Possible reasons:")
                print(f"    1. Actual distance is large (locations far apart)")
                print(f"    2. Speed setting ({self.avg_kph} km/h) is too low for Melbourne")
                print(f"    3. Coordinates might be incorrect (check lat/lon values)")
            
            elif avg_time > 30:  # Average more than 30 minutes
                print(f"  ⚠️  Average travel time is {avg_time:.1f} minutes")
                print(f"  Consider increasing speed from {self.avg_kph} km/h if locations are nearby")
            else:
                print(f"  ✓ Travel times look reasonable for Melbourne area")
        
        print(f"{'='*80}")
        print(f"OR-TOOLS SOLVER SETUP")
        print(f"{'='*80}")
        print(f"Distance matrices built: K={K} techs, I={I} requests")
        
        # Node indices
        start_nodes = list(range(K))
        cust_base = K
        num_nodes = K + I
        print(f"Nodes: start_nodes={start_nodes}, cust_base={cust_base}, num_nodes={num_nodes}")
        
        # Time windows (in minutes from reference time)
        # Convert time objects to datetime for comparison
        from datetime import datetime as dt
        from django.utils import timezone
        
        # Ensure date_anchor is a date object
        date_anchor = assigned_date.date() if hasattr(assigned_date, 'date') else assigned_date
        
        # Convert all times to aware datetime
        from datetime import time as time_cls
        window_starts = []
        for req in reqs:
            if hasattr(req.window_start, 'replace'):
                # It's a datetime object
                if timezone.is_aware(req.window_start):
                    window_starts.append(req.window_start)
                else:
                    window_starts.append(timezone.make_aware(req.window_start))
            elif isinstance(req.window_start, time_cls):
                window_starts.append(timezone.make_aware(dt.combine(date_anchor, req.window_start)))
            else:
                window_starts.append(req.window_start)
        
        shift_starts = []
        for tech in techs:
            if isinstance(tech.shift_start, time_cls):
                dt_obj = dt.combine(date_anchor, tech.shift_start)
                # Make timezone-aware
                if not timezone.is_aware(dt_obj):
                    dt_obj = timezone.make_aware(dt_obj)
                shift_starts.append(dt_obj)
            elif hasattr(tech.shift_start, 'replace'):
                if not timezone.is_aware(tech.shift_start):
                    shift_starts.append(timezone.make_aware(tech.shift_start))
                else:
                    shift_starts.append(tech.shift_start)
            else:
                shift_starts.append(tech.shift_start)
        
        earliest = min(window_starts + shift_starts)
        
        def mins_from_ref(dt_obj):
            # Ensure dt_obj is timezone-aware
            if isinstance(dt_obj, time_cls):
                dt_obj_combined = dt.combine(date_anchor, dt_obj)
                if not timezone.is_aware(dt_obj_combined):
                    dt_obj_combined = timezone.make_aware(dt_obj_combined)
            elif hasattr(dt_obj, 'replace'):
                if not timezone.is_aware(dt_obj):
                    dt_obj_combined = timezone.make_aware(dt_obj)
                else:
                    dt_obj_combined = dt_obj
            else:
                dt_obj_combined = dt_obj
            
            delta = dt_obj_combined - earliest
            return int(round(delta.total_seconds() / 60.0))
        
        tw_start = {}
        tw_end = {}
        
        for n in range(num_nodes):
            if n in start_nodes:
                k = n
                # Convert time objects to datetime
                if isinstance(techs[k].shift_start, time_cls):
                    shift_start_dt = dt.combine(date_anchor, techs[k].shift_start)
                    if not timezone.is_aware(shift_start_dt):
                        shift_start_dt = timezone.make_aware(shift_start_dt)
                elif hasattr(techs[k].shift_start, 'replace'):
                    shift_start_dt = techs[k].shift_start
                    if not timezone.is_aware(shift_start_dt):
                        shift_start_dt = timezone.make_aware(shift_start_dt)
                else:
                    shift_start_dt = techs[k].shift_start
                
                if isinstance(techs[k].shift_end, time_cls):
                    shift_end_dt = dt.combine(date_anchor, techs[k].shift_end)
                    if not timezone.is_aware(shift_end_dt):
                        shift_end_dt = timezone.make_aware(shift_end_dt)
                elif hasattr(techs[k].shift_end, 'replace'):
                    shift_end_dt = techs[k].shift_end
                    if not timezone.is_aware(shift_end_dt):
                        shift_end_dt = timezone.make_aware(shift_end_dt)
                else:
                    shift_end_dt = techs[k].shift_end
                
                tw_start[n] = mins_from_ref(shift_start_dt)
                tw_end[n] = mins_from_ref(shift_end_dt)
            else:
                i = n - cust_base
                # reqs[i].window_start and window_end should already be datetime
                window_start_dt = reqs[i].window_start
                if hasattr(window_start_dt, 'replace') and not timezone.is_aware(window_start_dt):
                    window_start_dt = timezone.make_aware(window_start_dt)
                
                window_end_dt = reqs[i].window_end
                if hasattr(window_end_dt, 'replace') and not timezone.is_aware(window_end_dt):
                    window_end_dt = timezone.make_aware(window_end_dt)
                
                tw_start[n] = mins_from_ref(window_start_dt)
                tw_end[n] = mins_from_ref(window_end_dt)
        
        # Service times and capacities
        service = {(cust_base + i): reqs[i].service_minutes for i in range(I)}
        capacities = [t.capacity_minutes for t in techs]
        demands = {(cust_base + i): reqs[i].service_minutes for i in range(I)}
        
        # Get existing assignments for each technician on the assigned date
        # This prevents double-booking technicians who already have jobs
        existing_assignments_by_tech = {}
        for k, tech in enumerate(techs):
            existing = Assignment.objects.filter(
                technician=tech,
                assigned_date=assigned_date.date(),
                status__in=['assigned', 'in_progress']
            ).select_related('service_request')
            
            # Store time windows of existing assignments
            existing_windows = []
            for assign in existing:
                # Convert to minutes from reference
                planned_start_mins = mins_from_ref(assign.planned_start)
                planned_finish_mins = mins_from_ref(assign.planned_finish) + assign.service_request.service_minutes
                existing_windows.append((planned_start_mins, planned_finish_mins))
            
            existing_assignments_by_tech[k] = existing_windows
        
        print(f"\nExisting assignments check:")
        for k, tech in enumerate(techs):
            if existing_assignments_by_tech[k]:
                print(f"  Tech {k} ({tech.user.username}): {len(existing_assignments_by_tech[k])} existing assignment(s)")
        
        # Skills matching - inspired by Gurobi technician routing
        # Only allow technicians with the required skill AND available time slots
        allowed_vehicles = {}
        for i, req in enumerate(reqs):
            allowed = []
            required_skill = req.required_skill if hasattr(req, 'required_skill') else None
            
            # Get request time window in minutes
            req_start_mins = tw_start[cust_base + i]
            req_end_mins = tw_end[cust_base + i]
            req_duration = req.service_minutes
            
            if required_skill:
                # Only allow technicians with the required skill
                for k, t in enumerate(techs):
                    if t.skills.filter(id=required_skill.id).exists():
                        # Check 1: Technician shift overlaps with customer window
                        if tw_start[cust_base + i] <= tw_end[k] and tw_end[cust_base + i] >= tw_start[k]:
                            # Check 2: No existing assignments conflict (technician is available)
                            has_conflict = False
                            for existing_start, existing_end in existing_assignments_by_tech[k]:
                                # Check if request window overlaps with existing assignment
                                # Overlap if: req_start < existing_end AND req_end > existing_start
                                if req_start_mins < existing_end and (req_start_mins + req_duration) > existing_start:
                                    has_conflict = True
                                    print(f"  Tech {k} ({t.user.username}) has conflict: existing ({existing_start}-{existing_end}) vs request ({req_start_mins}-{req_start_mins + req_duration})")
                                    break
                            
                            if not has_conflict:
                                allowed.append(k)
                        else:
                            print(f"Request {i} ({req.name}) needs '{required_skill.name}' but tech {k} ({t.user.username}) has incompatible shift time window")
                
                if not allowed:
                    print(f"WARNING: No technician has required skill '{required_skill.name}' with available time slot for request {i}")
                    # Don't allow all - let the job be dropped if no matching tech
                else:
                    print(f"Request {i} ({req.name}) needs skill '{required_skill.name}', allowed techs: {allowed}")
            else:
                # No skill requirement - check time window compatibility and availability
                for k, t in enumerate(techs):
                    if tw_start[cust_base + i] <= tw_end[k] and tw_end[cust_base + i] >= tw_start[k]:
                        # Check if technician has available time slot
                        has_conflict = False
                        for existing_start, existing_end in existing_assignments_by_tech[k]:
                            if req_start_mins < existing_end and (req_start_mins + req_duration) > existing_start:
                                has_conflict = True
                                break
                        
                        if not has_conflict:
                            allowed.append(k)
                
                if not allowed:
                    print(f"WARNING: Request {i} ({req.name}) has no available technician with compatible time window")
                else:
                    print(f"Request {i} has no skill requirement, allowing all {len(allowed)} techs with available time slots")
            
            allowed_vehicles[cust_base + i] = allowed

        print(f"\nSummary of allowed vehicles:")
        for i in range(I):
            node = cust_base + i
            allowed = allowed_vehicles.get(node, [])
            req_name = reqs[i].name
            print(f"  Request '{req_name}' (node {node}): allowed techs = {allowed}")
        sys.stdout.flush()
        
        # Create manager and routing
        manager = pywrapcp.RoutingIndexManager(num_nodes, K, start_nodes, start_nodes)
        routing = pywrapcp.RoutingModel(manager)
        
        def time_callback(from_index, to_index):
            a = manager.IndexToNode(from_index)
            b = manager.IndexToNode(to_index)
            travel = 0
            svc = service.get(a, 0)
            
            if a in start_nodes and (cust_base <= b < cust_base + I):
                k = a
                i = b - cust_base
                travel = int(round(t_s_i[(k, i)]))
            elif (cust_base <= a < cust_base + I) and (cust_base <= b < cust_base + I):
                i = a - cust_base
                j = b - cust_base
                travel = int(round(t_i_j[(i, j)]))
            elif (cust_base <= a < cust_base + I) and b in start_nodes:
                i = a - cust_base
                k = b
                travel = int(round(t_i_e[(k, i)]))
            
            return travel + svc
        
        transit_cb_idx = routing.RegisterTransitCallback(time_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_cb_idx)
        
        # Add time dimension
        # Use a longer horizon to accommodate all possible time windows
        # Check the maximum time window value
        max_window_end = max(tw_end.values()) if tw_end else 24 * 60
        horizon = max(24 * 60, int(max_window_end) + 60)  # At least 24 hours, more if needed
        
        print(f"Setting horizon to: {horizon} minutes (max_window_end={max_window_end})")
        sys.stdout.flush()
        routing.AddDimension(transit_cb_idx, 0, horizon, False, "Time")
        time_dim = routing.GetDimensionOrDie("Time")
        
        # Add time windows with validation
        print(f"\nAdding time windows...")
        import sys
        sys.stdout.flush()
        
        for node in range(num_nodes):
            try:
                index = manager.NodeToIndex(node)
                start = tw_start.get(node, 0)
                end = tw_end.get(node, horizon)
                
                # Validate time window
                if start > end:
                    print(f"ERROR: Node {node} has invalid time window: {start} > {end}")
                    sys.stdout.flush()
                    raise ValueError(f"Invalid time window for node {node}: start={start}, end={end}")
                
                # Check if it's within valid range
                if start < 0 or end > horizon:
                    print(f"WARNING: Node {node} time window outside horizon: start={start}, end={end}, horizon={horizon}")
                    print(f"  Clamping to valid range...")
                    sys.stdout.flush()
                    # Clamp to valid range
                    if start < 0:
                        start = 0
                    if end > horizon:
                        end = horizon
                
                # Final validation
                if start > end:
                    print(f"FATAL: After clamping, still invalid: start={start}, end={end}")
                    sys.stdout.flush()
                    raise ValueError(f"Invalid time window after clamping: start={start}, end={end}")
                
                time_dim.CumulVar(index).SetRange(start, end)
            except Exception as e:
                print(f"ERROR setting time window for node {node}: {str(e)}")
                print(f"  tw_start[{node}] = {tw_start.get(node, 'NOT SET')}")
                print(f"  tw_end[{node}] = {tw_end.get(node, 'NOT SET')}")
                sys.stdout.flush()
                import traceback
                traceback.print_exc()
                raise
        
        print(f"Time windows set successfully for {num_nodes} nodes")
        sys.stdout.flush()
        
        # Add capacity dimension
        def demand_callback(from_index):
            node = manager.IndexToNode(from_index)
            return demands.get(node, 0)
        
        demand_cb_idx = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(demand_cb_idx, 0, capacities, True, "Capacity")
        
        # Skills constraints
        for i, req in enumerate(reqs):
            node = cust_base + i
            allowed = set(allowed_vehicles[node])
            index = manager.NodeToIndex(node)
            for k in range(K):
                if k not in allowed:
                    routing.VehicleVar(index).RemoveValue(k)
        
        # Optional jobs with drop penalty
        drop_penalty = self.config.drop_penalty_per_job
        for i in range(I):
            node = cust_base + i
            routing.AddDisjunction([manager.NodeToIndex(node)], drop_penalty)
        
        # Search
        print(f"\n{'='*80}")
        print(f"SOLVING WITH OR-TOOLS")
        print(f"{'='*80}")
        print(f"Total time windows: {len([k for k in tw_start.keys() if k < cust_base])} techs, {len([k for k in tw_start.keys() if k >= cust_base])} requests")
        print(f"Time window ranges:")
        for k in range(num_nodes):
            if k in tw_start and k in tw_end:
                print(f"  Node {k}: {tw_start[k]} - {tw_end[k]} minutes")
        
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        # Optimize for nearby locations - use faster strategy first
        search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        
        # For nearby locations, reduce time limit and use simpler search
        # If all locations are nearby Melbourne, solver should find solution quickly
        time_limit = min(self.config.time_limit_seconds, 30)  # Max 30 seconds for nearby locations
        search_params.time_limit.FromSeconds(time_limit)
        
        # Use faster local search for nearby locations (TABU_SEARCH is faster than GUIDED_LOCAL_SEARCH)
        search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH
        
        print(f"Attempting to solve (time limit: {time_limit}s)...")
        import sys
        sys.stdout.flush()
        
        solver_start = time.time()
        
        # For nearby locations, try fastest strategy first
        solution = None
        strategies = [
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC,  # Fastest
            routing_enums_pb2.FirstSolutionStrategy.PATH_MOST_CONSTRAINED_ARC,  # Second fastest
        ]
        
        for strategy in strategies:
            try:
                search_params.first_solution_strategy = strategy
                strategy_start = time.time()
                print(f"Trying strategy: {strategy} (max {time_limit}s)")
                sys.stdout.flush()
                solution = routing.SolveWithParameters(search_params)
                strategy_time = time.time() - strategy_start
                
                if solution:
                    total_solver_time = time.time() - solver_start
                    print(f"✓ Solution found with strategy: {strategy}")
                    print(f"  Strategy took: {strategy_time:.2f} seconds")
                    print(f"  Total solver time: {total_solver_time:.2f} seconds")
                    sys.stdout.flush()
                    break
                else:
                    print(f"  Strategy returned no solution in {strategy_time:.2f}s")
                    sys.stdout.flush()
            except Exception as e:
                strategy_time = time.time() - strategy_start
                print(f"  Strategy failed in {strategy_time:.2f}s: {str(e)}")
                import traceback
                traceback.print_exc()
                sys.stdout.flush()
                continue
        
        if solution is None:
            print("ERROR: OR-Tools returned no solution after trying all strategies")
            print(f"Parameters: K={K} techs, I={I} requests, num_nodes={num_nodes}")
            print("This means the solver could not find a valid assignment.")
            print("Possible reasons:")
            print("  - No technicians match the required skills")
            print("  - Time windows are incompatible")
            print("  - Service requests exceed technician capacity")
            sys.stdout.flush()
            return [], reqs, 0.0
        
        print(f"Solver result: Solution found")
        sys.stdout.flush()
        
        # Extract solution
        extraction_start = time.time()
        print(f"\nExtracting assignments from solution...")
        sys.stdout.flush()
        assignments = []
        served_ids = set()
        
        for k in range(K):
            idx = routing.Start(k)
            order = 0
            route_assignments = []
            
            print(f"Tech {k} ({techs[k].user.username}):")
            step = 0
            while not routing.IsEnd(idx):
                node = manager.IndexToNode(idx)
                print(f"  Step {step}: node={node} (cust_base={cust_base}, I={I})")
                if cust_base <= node < cust_base + I:
                    order += 1
                    req = reqs[node - cust_base]
                    try:
                        t_start_min = solution.Value(time_dim.CumulVar(idx))
                        start_dt = earliest + timedelta(minutes=t_start_min)
                        finish_dt = start_dt + timedelta(minutes=req.service_minutes)
                        
                        print(f"  Assignment {order}: {req.name} at {start_dt.strftime('%Y-%m-%d %H:%M')}")
                    except Exception as e:
                        print(f"  ERROR extracting assignment for node {node}: {e}")
                        break
                    
                    assignments.append({
                        'service_request': req,
                        'technician': techs[k],
                        'assigned_date': assigned_date.date(),
                        'sequence_order': order,
                        'planned_start': start_dt,
                        'planned_finish': finish_dt,
                        'travel_time': 0.0
                    })
                    served_ids.add(req.id)
                
                idx = solution.Value(routing.NextVar(idx))
                step += 1
            
            if not route_assignments:
                print(f"  No assignments for this tech")
            sys.stdout.flush()
        
        extraction_time = time.time() - extraction_start
        print(f"Extracted {len(assignments)} assignments in {extraction_time:.3f}s")
        sys.stdout.flush()
        
        unserved = [req for req in reqs if req.id not in served_ids]
        unserved_with_reasons = []
        
        print(f"\n{'='*80}")
        print(f"ASSIGNMENT VERIFICATION")
        print(f"{'='*80}")
        print(f"Total requests: {len(reqs)}")
        print(f"Assigned: {len(assignments)}")
        print(f"Unserved: {len(unserved)}")
        
        if unserved:
            print(f"\nUnserved requests and reasons:")
            for req in unserved:
                req_idx = reqs.index(req)
                node = cust_base + req_idx
                allowed_techs = allowed_vehicles.get(node, [])
                required_skill = req.required_skill.name if req.required_skill else 'None'
                reason_detail = ""
                reason_short = ""
                
                if not allowed_techs:
                    # Check why no techs allowed
                    if required_skill != 'None':
                        # Find techs with this skill
                        techs_with_skill = [k for k, t in enumerate(techs) if t.skills.filter(name=required_skill).exists()]
                        if not techs_with_skill:
                            reason_short = "No technician with required skill"
                            reason_detail = f"No technician has the required skill '{required_skill}'"
                        else:
                            # Check time windows
                            time_incompatible = []
                            compatible_techs = []
                            for k in techs_with_skill:
                                tech = techs[k]
                                # Check if time windows overlap
                                if tw_start[node] <= tw_end[k] and tw_end[node] >= tw_start[k]:
                                    # Time windows overlap, check other constraints
                                    compatible_techs.append(k)
                                else:
                                    time_incompatible.append(k)
                            
                            if len(compatible_techs) == 0:
                                # All techs with skill have incompatible time windows
                                tech_names = [techs[k].user.username for k in techs_with_skill[:3]]
                                reason_short = "Time window mismatch"
                                reason_detail = f"Technicians with skill '{required_skill}' ({', '.join(tech_names)}{'...' if len(techs_with_skill) > 3 else ''}) have shifts that don't overlap with the requested time window"
                            else:
                                reason_short = "Capacity or routing constraint"
                                reason_detail = f"Skill '{required_skill}' available, but no technician could be assigned due to capacity limits or routing constraints"
                    else:
                        # No skill requirement
                        reason_short = "No compatible time windows"
                        reason_detail = "No technician has a shift that overlaps with the requested time window"
                else:
                    # Some techs allowed but not assigned
                    tech_names = [techs[k].user.username for k in allowed_techs]
                    reason_short = "Capacity exhausted"
                    reason_detail = f"Technicians {', '.join(tech_names[:3])}{'...' if len(tech_names) > 3 else ''} are compatible but don't have enough capacity or routing conflicts"
                
                unserved_info = {
                    'request': req,
                    'reason_short': reason_short,
                    'reason_detail': reason_detail,
                    'required_skill': required_skill,
                    'allowed_technicians': [techs[k].user.username for k in allowed_techs] if allowed_techs else []
                }
                unserved_with_reasons.append(unserved_info)
                
                print(f"  - {req.name}")
                print(f"    Required skill: {required_skill}")
                print(f"    Reason: {reason_detail}")
                if allowed_techs:
                    tech_names = [techs[k].user.username for k in allowed_techs]
                    print(f"    Allowed techs: {', '.join(tech_names)}")
        else:
            print(f"\n✓ All requests successfully assigned!")
        
        # Verify skill matching for assigned jobs
        print(f"\n✓ Skill matching verification for assigned jobs:")
        skill_match_errors = []
        for assignment in assignments:
            req = assignment['service_request']
            tech = assignment['technician']
            required_skill = req.required_skill
            
            if required_skill:
                if not tech.skills.filter(id=required_skill.id).exists():
                    skill_match_errors.append(
                        f"ERROR: {req.name} assigned to {tech.user.username} but tech doesn't have skill '{required_skill.name}'"
                    )
        
        if skill_match_errors:
            for error in skill_match_errors:
                print(f"  ✗ {error}")
        else:
            print(f"  ✓ All {len(assignments)} assignments have matching skills!")
        
        print(f"{'='*80}\n")
        sys.stdout.flush()
        
        # Calculate total travel time
        total_travel = 0.0
        for k in range(K):
            tech_assignments = [a for a in assignments if a['technician'] == techs[k]]
            if tech_assignments:
                if tech_assignments:
                    first = tech_assignments[0]
                    total_travel += t_s_i.get((k, first['service_request'].id - 1), 0.0)
                    for a in tech_assignments[1:]:
                        prev_idx = assignments.index(a) - 1
                        if prev_idx >= 0:
                            prev = assignments[prev_idx]
                            total_travel += t_i_j.get((prev_idx, prev_idx + 1), 0.0)
        
        # Print total time summary
        solver_end_time = time.time()
        total_time = solver_end_time - start_time
        solver_total_time = solver_end_time - solver_start
        
        print(f"\n{'='*80}")
        print(f"⏱️  TIME SUMMARY")
        print(f"{'='*80}")
        print(f"Distance matrix calculation: {matrix_time:.3f}s ({K*I*2 + I*I} calculations, Haversine formula)")
        print(f"Solver execution: {solver_total_time:.3f}s (OR-Tools CP-SAT solver)")
        print(f"Assignment extraction: {extraction_time:.3f}s (parsing solution)")
        print(f"{'─'*60}")
        print(f"TOTAL TIME: {total_time:.3f}s")
        print(f"{'='*80}\n")
        
        return assignments, unserved_with_reasons, total_travel

