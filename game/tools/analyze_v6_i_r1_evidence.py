#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, pathlib
from typing import Any

CANDIDATES = [
    f"V6_D{d}_R{r}_S{s}"
    for d in (20,25,30) for r in (35,45) for s in ("08","10")
]
PAIR_BASES = [f"V6_D{d}_R{r}" for d in (20,25,30) for r in (35,45)]
EXCLUDED_PAIR_FIELDS = {
    "candidate_id", "desired_speed_mps", "planned_speed_cap_mps",
    "slowdown_window_tick_count", "slowdown_window_cumulative_speed_change_mps",
}
COMMAND_FIELDS = ("commanded_throttle","commanded_brake","commanded_steer")
DYNAMICS_FIELDS = (
    "physics_tick","vector_tick","chainage_m","route_lateral_distance_m",
    "signed_lateral_error_m","lateral_velocity_mps","observed_speed_mps",
    "velocity_course_angle_rad","course_error_rad","requested_lateral_accel_mps2",
    "body_lead_angle_rad","predicted_lateral_error_m","recovery_phase",
)

def load(path:pathlib.Path)->Any:
    return json.loads(path.read_text(encoding="utf-8"))

def events(path:pathlib.Path)->list[dict[str,Any]]:
    out=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        value=json.loads(line)
        if isinstance(value,dict): out.append(value)
    return out

def projections(path:pathlib.Path)->list[dict[str,Any]]:
    return [value for value in events(path) if value.get("event")=="TEST_DRIVER_ROUTE_PROJECTION"]

def first(rows, predicate):
    return next((r for r in rows if predicate(r)), None)

def snapshot(r:dict[str,Any]|None, fields:list[str])->dict[str,Any]|None:
    if r is None:return None
    return {k:r.get(k) for k in fields}

def transition_count(rows:list[dict[str,Any]], key:str, transform=lambda x:x)->int:
    if not rows:return 0
    values=[transform(r.get(key)) for r in rows]
    return sum(a!=b for a,b in zip(values,values[1:]))

def sha(path:pathlib.Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--evidence-root",required=True); ap.add_argument("--output"); args=ap.parse_args()
    root=pathlib.Path(args.evidence_root).resolve()
    gate=load(root/"gate_result.json"); copied=load(root/"COPY_SELECTED_PROJECT/result.json"); engine=load(root/"ENGINE_IDENTITY/result.json")
    milestones={}; streams={}
    for cid in CANDIDATES:
        d=root/"V6_A1_DEVELOPMENT"/cid/"runtime_vectors"/"RT_ROUTE_A1"
        all_events=events(d/"events.jsonl"); rows=[value for value in all_events if value.get("event")=="TEST_DRIVER_ROUTE_PROJECTION"]; streams[cid]=rows
        raw=load(d/"runtime_result.json"); suite=load(d/"suite_classification.json")
        first_brake=first(rows,lambda r:float(r.get("commanded_brake",0))>0.5)
        first_sat=first(rows,lambda r:abs(float(r.get("requested_lateral_accel_mps2",0)))>=11.5-1e-9)
        first_rec=first(rows,lambda r:bool(r.get("recovery_active",False)))
        first_5=first(rows,lambda r:abs(float(r.get("signed_lateral_error_m",0)))>=5.0)
        term=rows[-1]
        base_fields=["physics_tick","chainage_m","observed_speed_mps","desired_speed_mps","commanded_throttle","commanded_brake","recovery_phase"]
        lat_fields=base_fields+["signed_lateral_error_m","lateral_velocity_mps","course_error_rad","requested_lateral_accel_mps2","body_lead_angle_rad"]
        milestones[cid]={
            "candidate_id":cid,"physics_ticks":raw.get("physics_ticks"),"projection_count":len(rows),
            "peak_speed_mps":raw.get("peak_horizontal_speed_mps"),"fast_distance_m":raw.get("distance_at_or_above_fast_speed_m"),
            "maximum_deviation_m":raw.get("maximum_lateral_error_m", raw.get("test_driver_route_projection",{}).get("maximum_route_lateral_distance_m")),
            "hard_collisions":raw.get("hard_collisions"),"post_result_event_count":suite.get("post_result_event_count"),
            "first_braking":snapshot(first_brake,base_fields),"first_lateral_saturation":snapshot(first_sat,lat_fields),
            "first_recovery":snapshot(first_rec,lat_fields),"first_5m_deviation":snapshot(first_5,lat_fields),
            "terminal":snapshot(term,lat_fields+["predicted_lateral_error_m","slowdown_healthy"]),
            "brake_switches":transition_count(rows,"commanded_brake",lambda x:float(x or 0)>0.5),
            "phase_switches":transition_count(rows,"recovery_phase"),
            "termination_reason":raw.get("termination_evidence",{}).get("reason"),
            "route_states":[r for r in all_events if r.get("event")=="ROUTE_STATE"],
        }
    pairs=[]
    for base in PAIR_BASES:
        a_id,b_id=base+"_S08",base+"_S10"; aa,bb=streams[a_id],streams[b_id]
        common=min(len(aa),len(bb)); differences=[]
        for i in range(common):
            keys=(set(aa[i])|set(bb[i]))-EXCLUDED_PAIR_FIELDS
            diff=[k for k in sorted(keys) if aa[i].get(k)!=bb[i].get(k)]
            if diff:
                differences.append({"index":i,"fields":diff[:20]})
                if len(differences)>=5:break
        pairs.append({
            "pair":[a_id,b_id],"same_length":len(aa)==len(bb),"projection_count":common,
            "nonexcluded_difference_count":len(differences),"first_differences":differences,
            "commands_tick_identical":all(all(aa[i].get(k)==bb[i].get(k) for k in COMMAND_FIELDS) for i in range(common)) and len(aa)==len(bb),
            "dynamics_tick_identical":all(all(aa[i].get(k)==bb[i].get(k) for k in DYNAMICS_FIELDS) for i in range(common)) and len(aa)==len(bb),
        })
    output={
        "schema":"district_zero.p1a.v1_2_4j.v6_raw_evidence_recompute.v1",
        "source_evidence":{
            "terminal_status":gate.get("status"),"terminal_stage":gate.get("terminal_stage"),
            "primary_failure_class":gate.get("details",{}).get("primary_failure_class"),
            "copied_source_file_count":copied.get("source_file_count"),"copied_byte_identical_file_count":copied.get("byte_identical_file_count"),
            "exact_godot":engine.get("observed"),
        },
        "candidate_count":len(CANDIDATES),"distinct_trajectory_count":sum(1 for p in pairs if p["commands_tick_identical"] and p["dynamics_tick_identical"]),
        "pair_identity":pairs,"candidate_milestones":milestones,
    }
    text=json.dumps(output,indent=2,sort_keys=True)+"\n"
    if args.output:pathlib.Path(args.output).write_text(text,encoding="utf-8",newline="\n")
    else:print(text,end="")
    return 0
if __name__=="__main__":raise SystemExit(main())
