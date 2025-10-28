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
        
        # Build travel time matrices
        t_s_i = {}  # Tech depot to customer
        t_i_j = {}  # Customer to customer
        t_i_e = {}  # Customer to depot
        
        # Validate data and calculate matrices
        import math
        
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
        
        print(f"\n{'='*80}")
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
        
        # Skills matching
        allowed_vehicles = {}
        for i, req in enumerate(reqs):
            # Service request now has single required_skill
            required_skill = req.required_skill if hasattr(req, 'required_skill') else None
            if required_skill:
                # Get the skill object and check if any technician has it
                allowed = []
                for k, t in enumerate(techs):
                    if t.skills.filter(id=required_skill.id).exists():
                        allowed.append(k)
                print(f"Request {i} ({req.name}) needs skill '{required_skill.name}', allowed techs: {allowed}")
                
                # If no tech has the required skill, allow all (job will be dropped later)
                if not allowed:
                    print(f"WARNING: No technician has required skill '{required_skill.name}' for request {i}")
                    allowed = list(range(K))  # Allow all, OR-Tools will handle drop penalty
            else:
                # No skill requirement, allow all technicians
                allowed = list(range(K))
                print(f"Request {i} has no skill requirement, allowing all {K} techs")
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
        search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        search_params.time_limit.FromSeconds(self.config.time_limit_seconds)
        
        print(f"Attempting to solve...")
        import sys
        sys.stdout.flush()  # Force flush output
        
        # Try multiple solution strategies if first fails
        solution = None
        
        strategies = [
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC,
            routing_enums_pb2.FirstSolutionStrategy.PATH_MOST_CONSTRAINED_ARC,
            routing_enums_pb2.FirstSolutionStrategy.SAVINGS,
            routing_enums_pb2.FirstSolutionStrategy.SWEEP,
        ]
        
        for strategy in strategies:
            try:
                search_params.first_solution_strategy = strategy
                print(f"Trying strategy: {strategy}")
                sys.stdout.flush()
                solution = routing.SolveWithParameters(search_params)
                if solution:
                    print(f"Solver found solution with strategy: {strategy}")
                    sys.stdout.flush()
                    break
                else:
                    print(f"Strategy {strategy} returned no solution")
                    sys.stdout.flush()
            except Exception as e:
                print(f"Strategy {strategy} failed: {str(e)}")
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
        assignments = []
        served_ids = set()
        
        for k in range(K):
            idx = routing.Start(k)
            order = 0
            
            while not routing.IsEnd(idx):
                node = manager.IndexToNode(idx)
                if cust_base <= node < cust_base + I:
                    order += 1
                    req = reqs[node - cust_base]
                    t_start_min = solution.Value(time_dim.CumulVar(idx))
                    start_dt = earliest + timedelta(minutes=t_start_min)
                    finish_dt = start_dt + timedelta(minutes=req.service_minutes)
                    
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
        
        unserved = [req for req in reqs if req.id not in served_ids]
        
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
        
        return assignments, unserved, total_travel

