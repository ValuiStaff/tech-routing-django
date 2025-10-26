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
        # Filter valid technicians and requests
        techs = [t for t in technicians if t.depot_lat is not None and t.depot_lon is not None]
        reqs = [r for r in service_requests if r.lat is not None and r.lon is not None and r.status == 'pending']
        
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
        
        for k in range(K):
            for i in range(I):
                t_s_i[(k, i)] = self.distance_service.travel_minutes(
                    techs[k].depot_lat, techs[k].depot_lon,
                    reqs[i].lat, reqs[i].lon,
                    self.avg_kph
                )
                t_i_e[(k, i)] = self.distance_service.travel_minutes(
                    reqs[i].lat, reqs[i].lon,
                    techs[k].depot_lat, techs[k].depot_lon,
                    self.avg_kph
                )
        
        for i in range(I):
            for j in range(I):
                if i == j:
                    t_i_j[(i, j)] = 0.0
                else:
                    t_i_j[(i, j)] = self.distance_service.travel_minutes(
                        reqs[i].lat, reqs[i].lon,
                        reqs[j].lat, reqs[j].lon,
                        self.avg_kph
                    )
        
        # Node indices
        start_nodes = list(range(K))
        cust_base = K
        num_nodes = K + I
        
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
            need = set(req.required_skills.all())
            allowed = [k for k, t in enumerate(techs) if (not need or need.issubset(set(t.skills.all())))]
            allowed_vehicles[cust_base + i] = allowed
        
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
        horizon = 24 * 60
        routing.AddDimension(transit_cb_idx, 0, horizon, False, "Time")
        time_dim = routing.GetDimensionOrDie("Time")
        
        for node in range(num_nodes):
            index = manager.NodeToIndex(node)
            time_dim.CumulVar(index).SetRange(tw_start[node], tw_end[node])
        
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
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        search_params.time_limit.FromSeconds(self.config.time_limit_seconds)
        
        solution = routing.SolveWithParameters(search_params)
        
        if solution is None:
            return [], reqs, 0.0
        
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

