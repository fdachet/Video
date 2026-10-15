


from __future__ import annotations

import copy
import csv
import hashlib
import ctypes
import datetime as _dt
import json
import math
import os
import queue
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import tempfile
import traceback
import urllib.error
import urllib.request
import uuid
import zlib
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable, Any
from ctypes import wintypes

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText


SERIAL_VERSION = "V266"
APP_NAME = f"Upscaler_{SERIAL_VERSION}"
SETTINGS_FILE = "Upscaler_V216_settings.json"
DURATION_HISTORY_FILE = "Upscaler_duration_history.csv"
TEMP_SPACE_GB_PER_MOVIE_HOUR = 200.0
TEMP_NVENC_CQ = 8
DEFAULT_SUCCESS_FOLDER = "OriginalDone"
DEFAULT_FAILED_FOLDER = "OriginalFailled"
DEFAULT_OUTPUT_FOLDER = "VideoUpscaled"
DURATION_HISTORY_COLUMNS = [
    "movie_id",
    "date_local",
    "day_local",
    "time_local",
    "history_schema_version",
    "file_size_bytes",
    "file_size_mb",
    "movie_length_seconds",
    "source_resolution",
    "source_width",
    "source_height",
    "source_fps",
    "source_frames",
    "fps_reduce_enabled",
    "fps_reduce_mode",
    "fps_reduce_value",
    "ai_input_fps",
    "ai_input_frames",
    "scale_factor",
    "algorithm",
    "algorithm_mode",
    "ai_output_resolution",
    "ai_output_width",
    "ai_output_height",
    "ai_output_pixels_per_frame",
    "ai_pixel_rate",
    "ai_workload_pixel_frames",
    "upscale_used",
    "seed_frames_per_batch",
    "seed_overlap",
    "seed_expected_meta_batches",
    "rife_used",
    "rife_multiplier",
    "rife_gpu_threads",
    "rife_input_fps",
    "rife_output_fps",
    "rife_input_frames",
    "rife_output_frames",
    "rife_generated_frames",
    "rife_pixels_per_frame",
    "rife_generated_pixel_frames",
    "final_encode_pixel_frames",
    "final_encoder",
    "final_quality",
    "final_quality_value",
    "final_encoder_threads",
    "expected_bitrate_mbps",
    "rife_pipeline_workload",
    "seed_nvidia_launch_mode",
    "seed_disable_dynamic_vram",
    "seed_disable_async_offload",
    "repair_enabled",
    "denoise_setting",
    "color_setting",
    "brightness_setting",
    "white_setting",
    "output_resolution",
    "output_width",
    "output_height",
    "processing_duration_seconds",
    "processing_duration_hms",
    "stage_probe_seconds",
    "stage_repair_seconds",
    "stage_fps_reduce_seconds",
    "stage_denoise_seconds",
    "stage_ai_seconds",
    "preseed_mode",
    "pre_neural_downscale_factor",
    "pre_neural_input_pixels",
    "preseed_factor",
    "seedvr2_factor",
    "stage_pre_neural_downscale_seconds",
    "stage_native_vsr_seconds",
    "stage_preseed_resize_seconds",
    "stage_seedvr2_seconds",
    "stage_enhancement_seconds",
    "stage_rife_seconds",
    "stage_encode_seconds",
    "stage_other_seconds",
    "observed_workload_per_second",
    "estimated_before_run_seconds",
    "raw_estimated_before_recalibration_seconds",
    "timing_recalibration_factor",
    "timing_recalibration_samples",
    "timing_recalibration_confidence_percent",
    "iterative_restoration_used",
    "iterative_restoration_plan_id",
    "iterative_restoration_target_factor",
    "iterative_restoration_ai_passes",
    "prediction_similarity_percent",
    "estimation_error_percent",
    "source_content_sha256",
    "source_fingerprint_schema",
    "configuration_sha256",
    "prediction_basis",
    "prediction_evidence",
    "seed_model_identifier",
    "native_vsr_model_identifier",

    "seed_requested_max_temporal_batch",
    "seed_requested_temporal_overlap",
    "seed_vae_tile_pixels",
    "seed_vae_spatial_overlap_pixels",
    "seed_requested_vae_tile",
    "seed_requested_vae_spatial_overlap",
    "seed_attempt_count",
    "seed_oom_retry_count",
    "seed_effective_frames_per_second",
    "seed_peak_dedicated_vram_gb_sampled",
    "seed_peak_shared_gpu_gb_sampled",
 
    "record_type",
    "seed_run_id",
    "seed_attempt_id",
    "seed_attempt_index",
    "seed_attempt_result",
    "seed_attempt_elapsed_seconds",
    "seed_attempt_effective_fps",
    "seed_observed_meta_batches",
    "seed_comfy_prompt_elapsed_seconds_sum",
    "seed_comfy_prompt_timing_events",
    "seed_gpu_utilization_percent_mean_sampled",
    "seed_gpu_samples_count",
    "seed_requested_batch_at_attempt",
    "seed_requested_overlap_at_attempt",
    "seed_dynamic_vram_enabled",
    "seed_async_offload_enabled",
    "seed_attention_backend_reported",
    "seed_blockswap_status",
    "seed_dit_compile_status",
    "seed_attempt_error_detail",
]

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".m4v", ".mpeg", ".mpg", ".mts",
    ".m2ts", ".ts", ".webm", ".wmv", ".flv", ".vob", ".3gp"
}

DOWNSCALE_CHOICES = [f"{x / 100:.2f}" for x in range(95, 9, -5)]

SEED_UPSCALE_CHOICES = [f"{n / 4:g}X" for n in range(4, 49)]  
SEED_TARGET_RESOLUTIONS = ["Use upscale factor", "720p", "1080p", "1440p", "2160p"]


FPS_REDUCE_MODES = ["Maximum FPS"]
FPS_MAX_FOR_AI_CHOICES = [30, 25, 20, 15, 10, 5, 1]
RIFE_MULTIPLIERS = [2, 3, 4, 6, 8, 10]
RIFE_GPU_THREADS_FIXED = 4
RIFE_MODES = ["Multiplier", "Target FPS"]
UPSCALE_CHOICES = SEED_UPSCALE_CHOICES
UPSCALE_ENGINES = ["SeedVR2"]
ALLOWED_FACTORS = [1.0] + [n / 2 for n in range(3, 25)]
TARGET_HEIGHTS = {"480p": 480, "720p": 720, "1080p": 1080, "1440p": 1440, "2160p": 2160}

ENHANCEMENT_STATES = ["Off", "Auto"]


SEED_REF_OUT_PIXELS = 1536 * 960
SEED_REF_BATCH = 49
SEED_REF_PIXEL_FRAMES = SEED_REF_OUT_PIXELS * SEED_REF_BATCH

SEED_AUTO_1080P_PIXEL_FRAMES = 1920 * 1080 * 37
SEED_PARAMETER_MODES = ("Auto (resolution-dependent)", "Manual")
SEED_BATCHES = [49, 45, 41, 37, 33, 29, 25, 21, 17, 13, 9, 5]

ENCODE_BACKENDS = ["NVIDIA NVENC (fast)", "libx265 CPU (best compression)"]
NVENC_QUALITY_PRESETS = ["Very Low", "Low", "Medium", "High"]
X265_QUALITY_PRESETS = ["Very Low", "Medium", "High", "Very High"]
NVENC_CQ_VALUES = {"Very Low": 36, "Low": 30, "Medium": 24, "High": 18}
X265_CRF_VALUES = {"Very Low": 30, "Medium": 24, "High": 20, "Very High": 16}
NVENC_EXPECTED_BITRATE_MULTIPLIERS = {"Very Low": 0.2975, "Low": 0.51, "Medium": 0.85, "High": 1.53}
X265_EXPECTED_BITRATE_MULTIPLIERS = {"Very Low": 0.2975, "Medium": 0.51, "High": 0.85, "Very High": 1.53}


PASTEL = {
    "bg": "#F7F5FB",
    "panel": "#FFFFFF",
    "blue": "#DCEBFA",
    "green": "#DDF2E4",
    "peach": "#FBE5D6",
    "purple": "#E9E0F6",
    "yellow": "#FFF3C9",
    "red": "#F8DADA",
    "text": "#2E3440",
    "muted": "#667085",
    "accent": "#8FB8DE",
    "accent2": "#9FC8A8",
    "warn": "#E7A95A",
    "error": "#C66A6A",
}



BASICVSR_RAM_WORKER_CODE = r'''
import argparse
import gc
import json
import struct
import sys
import time
import traceback
import numpy as np

def _read_exact(stream, n):
    out = bytearray(n)
    view = memoryview(out)
    position = 0
    while position < n:
        count = stream.readinto(view[position:])
        if not count:
            raise EOFError('Incomplete RAM video transport frame')
        position += count
    return out

def _write_all(writer, payload):
    view=memoryview(payload).cast('B')
    while len(view):
        count=writer.write(view)
        if count is None or count<=0:
            raise BrokenPipeError('BasicVSR++ RAM output pipe closed during frame')
        view=view[count:]

def _send_header(writer, data):
    block = json.dumps(data, separators=(',', ':')).encode('utf-8')
    _write_all(writer, struct.pack('>I', len(block)))
    _write_all(writer, block)
    writer.flush()

def _receive_header(reader):
    head = reader.read(4)
    if not head:
        return None
    if len(head) != 4:
        raise EOFError('Truncated worker request header')
    size = struct.unpack('>I', head)[0]
    if size < 2 or size > 100000:
        raise ValueError('Invalid worker request header size')
    return json.loads(bytes(_read_exact(reader, size)))

def _ramp(start, stop, core_start, core_stop, total, blend):
    xs = np.arange(start, stop, dtype=np.float32)
    out = np.ones(len(xs), dtype=np.float32)
    if core_start > 0:
        out *= np.clip((xs-(core_start-blend))/(2*blend), 0, 1)
    if core_stop < total:
        out *= np.clip(((core_stop+blend)-xs)/(2*blend), 0, 1)
    return out

def _tile_grid(width, height, core_w, core_h, halo):
    tiles=[]
    for cy in range(0, height, core_h):
        for cx in range(0, width, core_w):
            ex,ey = min(width,cx+core_w),min(height,cy+core_h)
            x0=max(0,((cx-halo)//4)*4)
            y0=max(0,((cy-halo)//4)*4)
            x1=min(width,((ex+halo+3)//4)*4)
            y1=min(height,((ey+halo+3)//4)*4)
            tiles.append((x0,y0,x1,y1,cx,cy,ex,ey))
    return tiles

def _profiles(which):
    fallback=[(384,216,48,12),(256,144,32,8),(192,108,24,6)]
    if str(which).startswith('Fast'):
        return [(768,432,64,16),(640,360,64,16),(512,288,64,16)] + fallback
    if str(which).startswith('Conservative'):
        return fallback
    return [(512,288,64,16)] + fallback

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',required=True)
    parser.add_argument('--checkpoint',required=True)
    args=parser.parse_args()
    # Only our framed binary protocol may write to stdout.
    wire_out=sys.stdout.buffer
    sys.stdout=sys.stderr
    wire_in=sys.stdin.buffer
    import torch
    from mmedit.apis import init_model
    from mmedit.core import tensor2img
    from mmedit.datasets.pipelines import Compose
    started=time.perf_counter()
    model=init_model(args.config,args.checkpoint,device=torch.device('cuda',0))
    model.eval()
    device=next(model.parameters()).device
    original_pipeline=(model.cfg.get('demo_pipeline') or
                       model.cfg.get('test_pipeline') or model.cfg.val_pipeline)
    prepared_pipeline=Compose([dict(x) for x in original_pipeline
                               if x.get('type') not in ('GenerateSegmentIndices','LoadImageFromFileList')])
    _send_header(wire_out,{'kind':'ready','load_seconds':round(time.perf_counter()-started,3)})

    def infer(frames, max_seq):
        # Match MMEditing's video-input route: RGB frames, rescale and
        # FramesToTensor via its actual config pipeline, not an approximation.
        data=prepared_pipeline({'lq':frames,'lq_path':None,'key':'memory_stream'})
        tensor=data['lq'].unsqueeze(0)
        with torch.inference_mode():
            if max_seq and tensor.size(1)>max_seq:
                pieces=[]
                for i in range(0,tensor.size(1),max_seq):
                    pieces.append(model(lq=tensor[:,i:i+max_seq].to(device),
                                        test_mode=True)['output'].cpu())
                output=torch.cat(pieces,dim=1)
            else:
                output=model(lq=tensor.to(device),test_mode=True)['output'].cpu()
        if output.ndim!=5 or int(output.shape[1])!=len(frames):
            raise RuntimeError('BasicVSR++ returned an unexpected frame sequence shape: '+str(tuple(output.shape)))
        return output

    def produce(frames, width, height, max_seq, profile):
        n=len(frames)
        if width*height<640*360:
            try:
                result=infer(frames,max_seq)
                if (int(result.shape[-1]),int(result.shape[-2]))!=(width*4,height*4):
                    raise RuntimeError('Model returned an invalid enlargement (must be exactly 4X).')
                out=[np.ascontiguousarray(tensor2img(result[:,i,:,:,:]).astype(np.uint8))
                     for i in range(n)]
                del result
                return out,'direct'
            except RuntimeError as exc:
                if not _is_oom(exc):
                    raise
                torch.cuda.empty_cache()
                gc.collect()
        failure=None
        for core_w,core_h,halo,blend in _profiles(profile):
            try:
                tiles=_tile_grid(width,height,core_w,core_h,halo)
                dest_w,dest_h=width*4,height*4
                # Bounded RAM: float32 accumulators; no tile or frame files.
                # Only a single frame-space weighting mask is needed.
                accum=np.zeros((n,dest_h,dest_w,3),dtype=np.float32)
                norm=np.zeros((dest_h,dest_w),dtype=np.float32)
                for x0,y0,x1,y1,cx,cy,ex,ey in tiles:
                    tile_frames=[np.ascontiguousarray(f[y0:y1,x0:x1]) for f in frames]
                    result=infer(tile_frames,max_seq)
                    if tuple(map(int,result.shape[-2:]))!=((y1-y0)*4,(x1-x0)*4):
                        raise RuntimeError('Native BasicVSR++ tile did not produce exactly 4X')
                    X0=max(0,cx*4-blend*4)
                    Y0=max(0,cy*4-blend*4)
                    X1=min(dest_w,ex*4+blend*4)
                    Y1=min(dest_h,ey*4+blend*4)
                    wx=_ramp(X0,X1,cx*4,ex*4,dest_w,blend*4)
                    wy=_ramp(Y0,Y1,cy*4,ey*4,dest_h,blend*4)
                    weight=wy[:,None]*wx[None,:]
                    norm[Y0:Y1,X0:X1]+=weight
                    crop_top=Y0-y0*4
                    crop_left=X0-x0*4
                    for i in range(n):
                        image=tensor2img(result[:,i,:,:,:]).astype(np.uint8)
                        image=image[crop_top:crop_top+Y1-Y0,crop_left:crop_left+X1-X0]
                        if image.shape[:2]!=(Y1-Y0,X1-X0):
                            raise RuntimeError('Neural tile crop geometry mismatch')
                        accum[i,Y0:Y1,X0:X1] += image.astype(np.float32)*weight[:,:,None]
                    del result,tile_frames
                if np.any(norm<=0):
                    raise RuntimeError('Uncovered output pixels after RAM tile blending')
                output=[]
                for i in range(n):
                    output.append(np.ascontiguousarray(np.clip(
                        np.rint(accum[i]/norm[:,:,None]),0,255).astype(np.uint8)))
                del accum,norm
                return output,f'{core_w}x{core_h}: {len(tiles)} tiles'
            except (RuntimeError,MemoryError) as exc:
                if not _is_oom(exc) and not isinstance(exc,MemoryError):
                    raise
                failure=str(exc)
                print('GPU/RAM OOM: retrying smaller neural spatial tiles: '+str(exc),
                      file=sys.stderr,flush=True)
                if 'accum' in locals(): del accum
                if 'norm' in locals(): del norm
                gc.collect()
                torch.cuda.empty_cache()
        raise RuntimeError('Native 4X BasicVSR++ failed even at minimum tile size: '+str(failure))

    def _is_oom(exc):
        message=str(exc).lower()
        return ('out of memory' in message or 'outofmemory' in message
                or 'cublas_status_alloc_failed' in message or 'not enough memory' in message)

    while True:
        request=_receive_header(wire_in)
        if request is None or request.get('action')=='quit':
            return
        if request.get('action')!='infer':
            _send_header(wire_out,{'kind':'error','message':'Unexpected action'})
            continue
        n=int(request['frames']);width=int(request['width']);height=int(request['height'])
        if not 1<=n<=120 or width<=0 or height<=0 or width*height>32000000:
            _send_header(wire_out,{'kind':'error','message':'Invalid shape/count'})
            continue
        frames=[]
        for i in range(n):
            raw=_read_exact(wire_in,width*height*3)
            frames.append(np.frombuffer(raw,dtype=np.uint8).reshape(height,width,3).copy())
        began=time.perf_counter()
        try:
            output,tiles=produce(frames,width,height,request.get('max_seq'),request.get('tile_profile','Balanced'))
            if len(output)!=n or any(f.shape!=(height*4,width*4,3) for f in output):
                raise RuntimeError('Native BasicVSR++ output verification failed')
            _send_header(wire_out,{'kind':'done','frames':n,'width':width*4,'height':height*4,
                                   'seconds':round(time.perf_counter()-began,3),'tiles':tiles})
            for frame in output:
                _write_all(wire_out, frame)
                wire_out.flush()
            del output
        except Exception:
            error=traceback.format_exc()[-14000:]
            print(error,file=sys.stderr,flush=True)
            _send_header(wire_out,{'kind':'error','message':error})
            gc.collect()
            if torch.cuda.is_available(): torch.cuda.empty_cache()
        finally:
            del frames
            gc.collect()

if __name__=='__main__':
    try:
        main()
    except Exception:
        print(traceback.format_exc(),file=sys.stderr,flush=True)
        raise
'''


class BasicVSRRamWorker:
    """Persistent model with framed RGB24/BGR24 pipes; zero frame-file writes."""

    def __init__(self, app, job, python_cmd, config, checkpoint, work_dir):
        self.app=app
        self.job=job
        self.work_dir=Path(work_dir).resolve()
        self.proc=None
        self.stderr_thread=None
        self.load_seconds=0.0
        self.inference_calls=0
        self.inference_seconds=0.0
        self.command=[str(python_cmd),'-u','-c',BASICVSR_RAM_WORKER_CODE,
                      '--config',str(config),'--checkpoint',str(checkpoint)]

    @staticmethod
    def _read_exact(stream, n):
        result=bytearray(n)
        view=memoryview(result)
        pos=0
        while pos<n:
            have=stream.readinto(view[pos:])
            if not have:
                raise BackendError(f'BasicVSR++ RAM pipe ended early: {pos}/{n} bytes')
            pos+=have
        return result

    @staticmethod
    def _write_all(stream, content):
        view=memoryview(content).cast('B')
        while len(view):
            count=stream.write(view)
            if count is None or count<=0:
                raise BackendError('BasicVSR++ RAM transport pipe stopped accepting bytes')
            view=view[count:]

    @classmethod
    def _receive_header(cls, pipe):
        import struct
        four=cls._read_exact(pipe,4)
        length=struct.unpack('>I',four)[0]
        if length<2 or length>100000:
            raise BackendError('Invalid BasicVSR++ RAM protocol length')
        return json.loads(bytes(cls._read_exact(pipe,length)))

    def _send_header(self, data):
        import struct
        content=json.dumps(data,separators=(',',':')).encode('utf-8')
        self._write_all(self.proc.stdin,struct.pack('>I',len(content)))
        self._write_all(self.proc.stdin,content)
        self.proc.stdin.flush()

    def start(self):
        self.app._post('log','V259 BASICVSR++: initializing persistent GPU model and RAM streams.')
        self.proc=subprocess.Popen(self.command,cwd=str(self.work_dir),
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
            bufsize=0,creationflags=self.app._no_window())
        with self.app.process_lock:
            self.app._aux_processes.append(self.proc)
        p=self.proc
        def collect_stderr():
            for raw in iter(p.stderr.readline,b''):
                line=raw.decode('utf-8',errors='replace').rstrip()
                if line:
                    self.app._post('log','BasicVSR++ GPU: '+line)
        self.stderr_thread=threading.Thread(target=collect_stderr,daemon=True)
        self.stderr_thread.start()
        status=self._receive_header(p.stdout)
        if status.get('kind')!='ready':
            raise BackendError('BasicVSR++ RAM worker failed to start: '+str(status))
        self.load_seconds=float(status.get('load_seconds',0.0))
        self.app._post('log',f'V259 BASICVSR++: loaded in {self.load_seconds:.2f}s; streaming raw RGB/BGR frames in RAM.')

    def infer_to_encoder(self, input_frames, width, height, profile, max_seq, writer):
        if self.proc is None or self.proc.poll() is not None:
            raise BackendError('BasicVSR++ RAM GPU worker exited unexpectedly')
        self._send_header({'action':'infer','frames':len(input_frames),
            'width':width,'height':height,'max_seq':max_seq,'tile_profile':profile})
        for frame in input_frames:
            if len(frame)!=width*height*3:
                raise BackendError('BasicVSR++ RGB input buffer has invalid dimensions')
            self._write_all(self.proc.stdin,frame)
        self.proc.stdin.flush()
        result=self._receive_header(self.proc.stdout)
        if result.get('kind')!='done':
            raise BackendError('BasicVSR++ RAM inference failed: '+str(result.get('message',result))[-4500:])
        if (result.get('frames'),result.get('width'),result.get('height'))!=(len(input_frames),width*4,height*4):
            raise BackendError('BasicVSR++ neural 4X frame count or resolution did not match input')
        frame_bytes=width*4*height*4*3
        for _ in input_frames:
            output=self._read_exact(self.proc.stdout,frame_bytes)
            self._write_all(writer,output)
        writer.flush()
        self.inference_calls+=1
        self.inference_seconds+=float(result.get('seconds',0.0))
        self.app._post('log',f'V259 BasicVSR++ RAM neural: {len(input_frames)} frames; '
                      f'{result.get("seconds")}s inference; tiles={result.get("tiles")}; '
                      'no temporary PNG output.')

    def stop(self):
        p=self.proc
        if p is None: return
        self.app._post('log',f'V259 BasicVSR++ GPU model reuse: load={self.load_seconds:.2f}s; '
                      f'chunks={self.inference_calls}; GPU inference={self.inference_seconds:.2f}s.')
        try:
            if p.poll() is None:
                try:
                    self._send_header({'action':'quit'})
                    p.wait(timeout=2.0)
                except Exception:
                    self.app._terminate_tree(p)
        finally:
            for ch in (p.stdin,p.stdout,p.stderr):
                if ch:
                    try: ch.close()
                    except Exception: pass
            with self.app.process_lock:
                if p in self.app._aux_processes:
                    self.app._aux_processes.remove(p)
            self.proc=None


@dataclass
class VideoInfo:
    path: Path
    width: int = 0
    height: int = 0
    fps: float = 0.0
    duration: float = 0.0
    frames: int = 0
    vcodec: str = ""
    acodec: str = ""
    video_bitrate: int = 0
    color_space: str = ""


@dataclass
class Job:
    info: VideoInfo
    original_path: Optional[Path] = None


    process_order: int = 0
    status: str = "Queued"
    stage: str = "waiting"
    progress: float = 0.0
    eta: str = "--"
    tree_id: str = ""
    final_path: Optional[Path] = None
    output_root: Optional[Path] = None
    engine_override: str = ""
    scale_choice_override: str = ""
    seed_target_resolution_override: str = ""
    ai_fps_override: float = 0.0
    section2_settings: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    started_at: float = 0.0
    estimated_seconds: Optional[float] = None
    raw_estimated_seconds: Optional[float] = None
    timing_recalibration_factor: float = 1.0
    timing_recalibration_samples: int = 0
    timing_recalibration_confidence: int = 0
    estimate_samples: int = 0
    estimate_similarity: int = 0
    estimate_similarity_text: str = "--"
    estimate_text: str = "Learning..."
    prediction_basis: str = "modeled"
    prediction_evidence: str = "Learning"
    history_source_sha256: str = ""
    history_configuration_sha256: str = ""
    history_seed_model_id: str = ""
    history_native_model_id: str = ""
    pre_run_overhead_seconds: float = 0.0


    ai_info: Optional[VideoInfo] = None
    fps_reduce_applied: bool = False
    verified_ai_output_width: int = 0
    verified_ai_output_height: int = 0


    seed_batch_used: int = 0
    seed_overlap_used: int = 0
    seed_expected_batches: int = 0
    seed_initial_batch_requested: str = ""
    seed_initial_overlap_requested: str = ""
    seed_initial_vae_tile_requested: str = ""
    seed_initial_vae_overlap_requested: str = ""
    seed_vae_tile_used: int = 0
    seed_vae_spatial_overlap_used: int = 0
    seed_attempt_count: int = 0
    seed_oom_retry_count: int = 0
    seed_benchmark_run_id: str = ""
    seed_peak_dedicated_vram_gb: float = 0.0
    seed_peak_shared_gpu_gb: float = 0.0

    stage_probe_seconds: float = 0.0
    stage_repair_seconds: float = 0.0
    deinterlace_applied: bool = False
    deinterlace_diagnostic: str = ""
    stage_fps_reduce_seconds: float = 0.0
    stage_denoise_seconds: float = 0.0
    stage_ai_seconds: float = 0.0
    stage_pre_neural_downscale_seconds: float = 0.0
    stage_native_vsr_seconds: float = 0.0
    native_vsr_frames_done: int = 0
    native_vsr_frames_expected: int = 0
    native_vsr_stage_eta_seconds: Optional[float] = None
    native_vsr_eta_reference_elapsed: float = 0.0
    stage_preseed_resize_seconds: float = 0.0
    stage_seedvr2_seconds: float = 0.0
    stage_enhancement_seconds: float = 0.0
    stage_rife_seconds: float = 0.0
    stage_encode_seconds: float = 0.0
    stage_other_seconds: float = 0.0

    elapsed_seconds: float = 0.0
    elapsed_text: str = "--"
    elapsed_display_bucket: int = -1
    resume_manifest_path: Optional[Path] = None
    resume_prior_elapsed_seconds: float = 0.0
    resume_prior_ai_seconds: float = 0.0
    persistent_resume_used: bool = False


class Cancelled(RuntimeError):
    pass


class BackendError(RuntimeError):
    pass


class VramSpillDetected(RuntimeError):
    pass


class UpscalerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} - SeedVR2 restoration with four-stage scaling")
        self.geometry("1630x1190")
        self.minsize(1330, 980)
        self.configure(bg=PASTEL["bg"])

        self.script_dir = Path(__file__).resolve().parent
        self.settings_path = self.script_dir / SETTINGS_FILE


        self.duration_history_path = self.script_dir / DURATION_HISTORY_FILE
        self._save_exit_checkpoint_in_progress = False
        self._save_exit_requested = False
        self._duration_history_lock = threading.RLock()
        self._duration_history_cache: Optional[List[Dict[str, str]]] = None
        self._duration_history_cache_mtime_ns: Optional[int] = None
        self._content_fingerprint_cache: Dict[Tuple[str, int, int], str] = {}
        self._checkpoint_fingerprint_cache: Dict[Tuple[str, int, int], str] = {}
        self._ensure_duration_history_file()

        self.jobs: List[Job] = []
        self.uiq: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self.stop_event = threading.Event()
        self.worker: Optional[threading.Thread] = None
        self.current_process: Optional[subprocess.Popen] = None
        self.process_lock = threading.Lock()


        self.pause_event = threading.Event()
        self._paused_process_pids: List[int] = []
        self._pause_started_at: Optional[float] = None
        self._resume_serial = 0
        self._pre_pause_step_text = ""
        self._pre_pause_eta_text = ""
        self._aux_processes: List[subprocess.Popen] = []

        self._autosave_after_id = None
        self._autosave_ready = False


        self._cpu_prev_times = None
        self._nvidia_smi_path = None


        self._spill_poll_busy = False
        self._spill_mib = None
        self._spill_delta_mib = 0.0
        self._shared_baseline_mib = None
        self._vram_total_mib = 0.0
        self._spill_warning_active = False
        self._spill_consecutive = 0


        self._seed_spill_trigger = False
        self._seed_active_batch = 0
        self._seed_batch_times: List[float] = []
        self._seed_last_prompt_seconds = 0.0


        self.comfy_proc: Optional[subprocess.Popen] = None
        self._comfy_running_mode: Optional[str] = None
        self._comfy_running_signature: Optional[Tuple[str, bool, bool]] = None


        self._comfy_runtime_port: Optional[int] = None


        self._comfy_runtime_root: Optional[Path] = None
        self._comfy_runtime_input_dir: Optional[Path] = None
        self._comfy_runtime_output_dir: Optional[Path] = None
        self._comfy_runtime_temp_dir: Optional[Path] = None
        self._comfy_runtime_dirs_to_cleanup: List[Path] = []
        self.comfy_console_thread: Optional[threading.Thread] = None
        self.comfy_final_event = threading.Event()
        self.comfy_final_path: Optional[Path] = None
        self.comfy_prompt_error: str = ""
        self.comfy_seed_progress = 0.0
        self.comfy_job_active = False
        self._seed_expected_meta_batches = 0
        self._seed_last_meta_batch = 0
        self._seed_meta_overrun = False


        self._seed_console_lock = threading.Lock()


        self._seed_console_active_token: Optional[str] = None
        self._seed_console_source_seen = False
        self._seed_console_final_by_token: Dict[str, Path] = {}
        self._comfy_generation = 0


        self._comfy_retained_inputs: List[Path] = []


        self._comfy_db_instance = uuid.uuid4().hex[:12]

        self.active_log_path: Optional[Path] = None


        self._run_engine: Optional[str] = None
        self._run_upscale_enable: Optional[bool] = None
        self._run_seed_upscale: Optional[str] = None
        self._run_seed_target_resolution: Optional[str] = None
        self._run_fps_reduce_enable: Optional[bool] = None
        self._run_fps_reduce_mode: Optional[str] = None
        self._run_fps_reduce_max: Optional[float] = None
        self._run_rife_enable: Optional[bool] = None
        self._run_rife_mode: Optional[str] = None
        self._run_rife_multiplier: Optional[str] = None
        self._run_rife_target_fps: Optional[float] = None
        self._run_move_processed_enable: Optional[bool] = None
        self._run_move_success_folder: Optional[str] = None
        self._run_move_failed_folder: Optional[str] = None
        self._run_comfy_launch_mode: Optional[str] = None
        self._run_comfy_disable_dynamic_vram: Optional[bool] = None
        self._run_comfy_disable_async_offload: Optional[bool] = None
        self._job_settings_context: Optional[Job] = None

        self.current_job_index = -1
        self.current_job_stage_fraction = 0.0
        self.current_job_stage_name = "idle"
        self.current_job_stage_weight_start = 0.0
        self.current_job_stage_weight = 0.0

        self._configure_style()
        self._build_vars()
        self._build_ui()
        self._load_settings()

        if self.seed_parameter_mode.get() == SEED_PARAMETER_MODES[0]:
            self.seed_batch_max.set("37")
            self.seed_temporal_overlap.set("2")
            self.seed_vae_tile.set("512")
            self.seed_vae_spatial_overlap.set("32")

        self.seed_upscale.set("1X")
        self.seedvr2_custom_factor.set("")
        self.seed_target_resolution.set("Use upscale factor")
        self.upscale_engine.set("SeedVR2")
        self.native_sr_enable.set(False)
        for _index in (1, 2, 3, 4):
            _method = getattr(self, f"scaling{_index}_method")
            _factor = getattr(self, f"scaling{_index}_factor")
            _target = getattr(self, f"scaling{_index}_target")
            if _method.get() not in ("Bicubic", "BasicVSR++ 4X (Blurry)", "RealBasicVSR 4X (Landscape)", "SeedVR2 restoration"):
                _method.set("Bicubic")
            if _method.get() != "Bicubic":
                _factor.set("1.00X" if _method.get() == "SeedVR2 restoration" else "4.00X")
                _target.set("Factor")
        self._initialize_section2_scoping()
        self._auto_detect_paths()
        self._update_controls()
        self._install_autosave_traces()
        for _v in (self.comfy_launch_mode, self.comfy_root, self.comfy_port):
            try:
                _v.trace_add("write", lambda *_: self._update_comfy_command_preview())
            except Exception:
                pass
        self._update_comfy_command_preview()
        for _v in (self.preseed_mode, self.native_sr_python, self.native_sr_repo,
                   self.native_sr_config, self.native_sr_checkpoint):
            _v.trace_add("write", lambda *_: self._schedule_files_status_refresh())
        self._autosave_ready = True
        self.after(250, self._refresh_files_status)
        self._schedule_save_settings()
        self.after(120, self._drain_uiq)
        self.after(1000, self._tick_eta)
        self.after(900, self._tick_resources)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Alt-F4>", self._on_alt_f4)
        


    def _configure_style(self):
        s = ttk.Style(self)
        self.ttk_style = s
        if "clam" in s.theme_names():
            s.theme_use("clam")
        s.configure(".", font=("Segoe UI", 9), background=PASTEL["bg"], foreground=PASTEL["text"])
        s.configure("TFrame", background=PASTEL["bg"])
        s.configure("TLabel", background=PASTEL["bg"], foreground=PASTEL["text"])
        s.configure("Header.TLabel", font=("Segoe UI", 17, "bold"), background=PASTEL["bg"], foreground=PASTEL["text"])
        s.configure("Sub.TLabel", foreground=PASTEL["muted"], background=PASTEL["bg"])
        s.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7))
        s.configure("Danger.TButton", font=("Segoe UI", 9, "bold"), padding=(10, 6))
        s.configure("Start.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7), background="#BFE8C4", foreground="#000000", bordercolor="#8FC79A", lightcolor="#BFE8C4", darkcolor="#BFE8C4", borderwidth=2)
        s.map("Start.TButton", background=[("active", "#A9DDB1"), ("pressed", "#96D2A0"), ("disabled", "#D5EAD8")], foreground=[("disabled", "#000000"), ("!disabled", "#000000")])
        s.configure("ProcessingActive.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7), background="#BFE8C4", foreground="#000000", bordercolor="#8FC79A", lightcolor="#BFE8C4", darkcolor="#BFE8C4", borderwidth=2, relief="solid")
        s.map("ProcessingActive.TButton", background=[("disabled", "#BFE8C4"), ("active", "#BFE8C4")], foreground=[("disabled", "#000000"), ("!disabled", "#000000")])
        s.configure("Stop.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7), background="#D64545", foreground="#000000", bordercolor="#AD3434", lightcolor="#D64545", darkcolor="#D64545")
        s.map("Stop.TButton", background=[("active", "#C63C3C"), ("pressed", "#A92F2F"), ("disabled", "#DDBBBB")], foreground=[("disabled", "#000000"), ("!disabled", "#000000")])
        s.configure("Pause.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7), background="#E8922E", foreground="#000000", bordercolor="#BC7321", lightcolor="#E8922E", darkcolor="#E8922E")
        s.map("Pause.TButton", background=[("active", "#D98224"), ("pressed", "#BB6E1B"), ("disabled", "#E4C9AA")], foreground=[("disabled", "#000000"), ("!disabled", "#000000")])
        s.configure("PausedActive.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7), background="#F3B869", foreground="#000000", bordercolor="#BC7321", lightcolor="#F3B869", darkcolor="#F3B869", borderwidth=2, relief="solid")
        s.map("PausedActive.TButton", background=[("disabled", "#F3B869"), ("active", "#F3B869")], foreground=[("disabled", "#000000"), ("!disabled", "#000000")])
        s.configure("Resume.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7), background="#2F80ED", foreground="#000000", bordercolor="#2367C1", lightcolor="#2F80ED", darkcolor="#2F80ED")
        s.map("Resume.TButton", background=[("active", "#2672D8"), ("pressed", "#1F5EB4"), ("disabled", "#B7CAE4")], foreground=[("disabled", "#000000"), ("!disabled", "#000000")])
        s.configure("SaveExit.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7), background="#C9F4F4", foreground="#000000", bordercolor="#8CCECE", lightcolor="#C9F4F4", darkcolor="#C9F4F4")
        s.map("SaveExit.TButton", background=[("active", "#B5EAEA"), ("pressed", "#A1DFDF"), ("disabled", "#DCEEEE")], foreground=[("disabled", "#000000"), ("!disabled", "#000000")])
        s.configure("OpenOutput.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7), background="#E2E2E2", foreground="#000000", bordercolor="#BFBFBF", lightcolor="#E2E2E2", darkcolor="#E2E2E2")
        s.map("OpenOutput.TButton", background=[("active", "#D5D5D5"), ("pressed", "#C8C8C8"), ("disabled", "#EEEEEE")], foreground=[("disabled", "#000000"), ("!disabled", "#000000")])
        s.configure("Pastel.TNotebook", background=PASTEL["bg"], borderwidth=0)
        s.configure("Pastel.TNotebook.Tab", padding=(14, 7), font=("Segoe UI", 9, "bold"))
        s.map("Pastel.TNotebook.Tab", background=[("selected", PASTEL["blue"]), ("!selected", "#EEEAF4")])


        for name, color in [
            ("Blue", PASTEL["blue"]), ("Green", PASTEL["green"]),
            ("Peach", PASTEL["peach"]), ("Purple", PASTEL["purple"]),
            ("Yellow", PASTEL["yellow"]), ("Red", PASTEL["red"]),
        ]:
            s.configure(f"{name}.TLabelframe", background=color, borderwidth=1, relief="solid")
            s.configure(f"{name}.TLabelframe.Label", background=color, foreground=PASTEL["text"], font=("Segoe UI", 10, "bold"))
            s.configure(f"{name}.TFrame", background=color)
            s.configure(f"{name}.TLabel", background=color, foreground=PASTEL["text"])
            s.configure(f"{name}.TCheckbutton", background=color, foreground=PASTEL["text"])
            s.configure(f"{name}.TRadiobutton", background=color, foreground=PASTEL["text"])

        s.configure("Files.Treeview", rowheight=18, font=("Segoe UI", 8))
        s.configure("Treeview", rowheight=24, background="#FFFFFF", fieldbackground="#FFFFFF", foreground=PASTEL["text"])
        s.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background=PASTEL["purple"])
        s.map("Treeview", background=[("selected", "#CFE3F6")], foreground=[("selected", PASTEL["text"])])
        s.configure("Horizontal.TProgressbar", troughcolor="#EAE7EF", background=PASTEL["accent"], thickness=17)


        s.configure("Spill.Horizontal.TProgressbar", troughcolor="#F7DEDE", background="#D94B4B", thickness=17)
        s.configure("Critical.Horizontal.TProgressbar", troughcolor="#F7DEDE", background="#D94B4B", thickness=17)
        s.configure("Spill.Red.TLabel", background=PASTEL["green"], foreground="#B00020", font=("Segoe UI", 9, "bold"))
        s.configure("Spill.Normal.TLabel", background=PASTEL["green"], foreground=PASTEL["text"], font=("Segoe UI", 9))

    def _build_vars(self):

        self.input_mode = tk.StringVar(value="file")
        self.input_path = tk.StringVar()
        self.recursive = tk.BooleanVar(value=False)
        self.output_parent = tk.StringVar()
        self.move_processed_enable = tk.BooleanVar(value=False)
        self.move_success_folder = tk.StringVar(value=DEFAULT_SUCCESS_FOLDER)
        self.move_failed_folder = tk.StringVar(value=DEFAULT_FAILED_FOLDER)


        self.fps_reduce_enable = tk.BooleanVar(value=False)
        self.fps_reduce_mode = tk.StringVar(value="Maximum FPS")
        self.fps_reduce_max = tk.DoubleVar(value=30.0)
        self.fps_reduce_preview = tk.StringVar(value="FPS Reduce: Off")

        self.enhancement_enable = tk.BooleanVar(value=True)
        self.repair_enable = tk.BooleanVar(value=True)
        self.deinterlace_auto = tk.BooleanVar(value=False)
        self.denoise = tk.StringVar(value="Off")
        self.color_correction = tk.StringVar(value="Off")
        self.brightness_correction = tk.StringVar(value="Off")
        self.white_correction = tk.StringVar(value="Off")
        self.sharpen = tk.StringVar(value="Off")
        self.deband = tk.StringVar(value="Off")
        self.upscale_engine = tk.StringVar(value="SeedVR2")
        self.upscale_enable = tk.BooleanVar(value=True)
        self.downscale_enable = tk.BooleanVar(value=False)
        self.downscale_preset = tk.StringVar(value="0.75")
        self.downscale_custom = tk.StringVar(value="")
        self.downscale_preview = tk.StringVar(value="Downscale is OFF. Enable to apply Lanczos reduction.")

        self.seed_upscale = tk.StringVar(value="1X")
        self.seedvr2_custom_factor = tk.StringVar(value="")
        self.seed_target_resolution = tk.StringVar(value="Use upscale factor")
        self.seed_parameter_mode = tk.StringVar(value="Auto (resolution-dependent)")
        self.seed_effective_summary = tk.StringVar(value="1080p (1X): batch 37 | temporal overlap 2 | VAE tile 512 | spatial overlap 32")
        self.seed_batch_max = tk.StringVar(value="37")
        self.seed_temporal_overlap = tk.StringVar(value="2")
        self.seed_vae_tile = tk.StringVar(value="512")
        self.seed_vae_spatial_overlap = tk.StringVar(value="32")
        self.comfy_disable_dynamic_vram = tk.BooleanVar(value=False)
        self.comfy_disable_async_offload = tk.BooleanVar(value=False)
        # Separate, opt-in true neural enlargement; never touches the V222 path when disabled.
        self.native_sr_enable = tk.BooleanVar(value=False)
        self.native_sr_model = tk.StringVar(value="RealBasicVSR_x4")
        self.native_sr_python = tk.StringVar(value=r"C:\Upscaler\RealBasicVSR_env\python.exe")
        self.native_sr_repo = tk.StringVar(value=r"C:\Upscaler\RealBasicVSR")
        self.native_sr_config = tk.StringVar(value=r"C:\Upscaler\RealBasicVSR\configs\realbasicvsr_x4.py")
        self.native_sr_checkpoint = tk.StringVar(value=r"C:\Upscaler\RealBasicVSR\checkpoints\RealBasicVSR_x4.pth")
        self.native_sr_max_seq_len = tk.StringVar(value="None")
        self.native_sr_chunk_frames = tk.StringVar(value="16")
        self.basicvsr_persistent_worker = tk.BooleanVar(value=True)
        self.basicvsr_tile_profile = tk.StringVar(value="Balanced (512x288)")

        self.preseed_mode = tk.StringVar(value="Only Bicubic")
        self.preseed_resolution = tk.StringVar(value="Factor")
        self.pre_neural_downscale_preset = tk.StringVar(value="1.00X")
        self.pre_neural_downscale_custom = tk.StringVar(value="")
        self.native_sr_preseed_preset = tk.StringVar(value="1X")
        self.native_sr_preseed_custom = tk.StringVar(value="")
        self.native_sr_scale_plan = tk.StringVar(value="Stage 1 → Stage 2 → Stage 3 | SeedVR2 1X available in any enabled stage")
        self.scaling_enable = tk.BooleanVar(value=True)
        self.scaling1_enabled = tk.BooleanVar(value=True)
        self.scaling1_method = tk.StringVar(value="Bicubic")
        self.scaling1_factor = tk.StringVar(value="1.00X")
        self.scaling1_target = tk.StringVar(value="Factor")
        self.scaling2_enabled = tk.BooleanVar(value=True)
        self.scaling2_method = tk.StringVar(value="Bicubic")
        self.scaling2_factor = tk.StringVar(value="1.00X")
        self.scaling2_target = tk.StringVar(value="Factor")
        self.scaling3_enabled = tk.BooleanVar(value=True)
        self.scaling3_method = tk.StringVar(value="Bicubic")
        self.scaling3_factor = tk.StringVar(value="1.00X")
        self.scaling3_target = tk.StringVar(value="Factor")
        self.scaling4_enabled = tk.BooleanVar(value=True)
        self.scaling4_method = tk.StringVar(value="Bicubic")
        self.scaling4_factor = tk.StringVar(value="1.00X")
        self.scaling4_target = tk.StringVar(value="Factor")
        self.upscale_size_choice = tk.StringVar(value="1X")
        self.force_exact_resolution = tk.BooleanVar(value=False)




        self.rife_enable = tk.BooleanVar(value=False)
        self.rife_mode = tk.StringVar(value="Multiplier")
        self.rife_multiplier = tk.StringVar(value="2X")
        self.rife_target_fps = tk.DoubleVar(value=50.0)
        self.rife_gpu_thread = tk.IntVar(value=RIFE_GPU_THREADS_FIXED)


        self.encode_backend = tk.StringVar(value="NVIDIA NVENC (fast)")
        self.encode_quality = tk.StringVar(value="Medium")
        self.x265_threads = tk.IntVar(value=max(1, min(12, os.cpu_count() or 1)))


        self.install_root = tk.StringVar(value=r"C:\Upscaler")
        self.ffmpeg = tk.StringVar(value="ffmpeg")
        self.ffprobe = tk.StringVar(value="ffprobe")
        self.comfy_root = tk.StringVar(value=r"C:\ComfyUI\ComfyUI_windows_portable_nvidia")
        self.comfy_launch_mode = tk.StringVar(value="NVIDIA Fast")


        self.comfy_command_preview = tk.StringVar(value="")
        self.workflow_json = tk.StringVar()
        self.comfy_port = tk.IntVar(value=8189)
        self.vspipe = tk.StringVar(value="vspipe")


        self.rife_plugin_dir = tk.StringVar()
        self.rife_plugin_dll = tk.StringVar()

        self.rife_model_path = tk.StringVar()

        self.vs_source_plugin_dll = tk.StringVar()


        self.current_file_text = tk.StringVar(value="Current file: --")
        self.current_step_text = tk.StringVar(value="Current step: idle")
        self.temp_path_text = tk.StringVar(value="Temporary files: H.264 NVENC very-high-quality intermediates; obsolete files auto-deleted when safe")
        self.temp_space_prediction = tk.StringVar(value="Predicted temporary space: scan videos to calculate queue peak")
        self.overall_progress = tk.DoubleVar(value=0.0)
        self.file_progress = tk.DoubleVar(value=0.0)
        self.eta_text = tk.StringVar(value="ETA: --")
        self.auto_bitrate_preview = tk.StringVar(value="Predicted bitrate: --")
        self.geometry_preview = tk.StringVar(value="Select/scan a video to preview output geometry.")
        self.comfy_status_text = tk.StringVar(value="Hidden ComfyUI: stopped")

        self.rife_status_text = tk.StringVar(value="RIFE: --")
        self._rife_runtime_active = False
        self._rife_runtime_output_fps = 0.0
        self._rife_runtime_gpu_thread = 0
        self._rife_runtime_gpu_name = ""
        self._gpu_name_cache = None

        self.cpu_usage = tk.DoubleVar(value=0.0)
        self.gpu_usage = tk.DoubleVar(value=0.0)
        self.vram_usage = tk.DoubleVar(value=0.0)
        self.vram_spill_usage = tk.DoubleVar(value=0.0)
        self.cpu_usage_text = tk.StringVar(value="CPU: --%")
        self.gpu_usage_text = tk.StringVar(value="GPU: --%")
        self.vram_usage_text = tk.StringVar(value="VRAM: -- / 12.0 GB")
        self.vram_spill_text = tk.StringVar(value="Shared GPU: -- GB")

        for v in (
            self.repair_enable, self.deinterlace_auto, self.denoise,
            self.color_correction, self.brightness_correction, self.white_correction,
            self.sharpen, self.deband,
            self.upscale_engine, self.upscale_enable, self.seed_upscale, self.seed_target_resolution,
            self.downscale_enable, self.downscale_preset, self.downscale_custom,
            self.force_exact_resolution,
            self.fps_reduce_enable, self.fps_reduce_mode, self.fps_reduce_max,
            self.rife_enable, self.rife_mode, self.rife_multiplier, self.rife_target_fps,
            self.rife_gpu_thread, self.comfy_launch_mode,
            self.encode_quality, self.x265_threads,
        ):
            v.trace_add("write", lambda *_: self._guarded_section2_refresh_preview())
        self.encode_backend.trace_add("write", lambda *_: self._guarded_section2_update_encode_controls())
        self.rife_enable.trace_add("write", lambda *_: self._guarded_section2_update_rife_controls())
        self.rife_mode.trace_add("write", lambda *_: self._guarded_section2_update_rife_controls())

        self.fps_reduce_enable.trace_add(
            "write",
            lambda *_: self._guarded_section2_update_fps_reduce_controls(),
        )
        self.fps_reduce_mode.trace_add(
            "write",
            lambda *_: self._guarded_section2_update_fps_reduce_controls(),
        )
        self.seed_upscale.trace_add("write", lambda *_: self._guarded_section2_update_upscale_controls())
        self.seedvr2_custom_factor.trace_add("write", lambda *_: self._guarded_section2_update_upscale_controls())
        self.preseed_mode.trace_add("write", lambda *_: self._preseed_mode_changed())
        self.preseed_resolution.trace_add("write", lambda *_: self._refresh_native_sr_scale_plan())
        self.preseed_resolution.trace_add("write", lambda *_: self._guarded_section2_refresh_preview())
        self.native_sr_preseed_custom.trace_add("write", lambda *_: self._preseed_custom_changed())
        for _pre_neural_var in (self.pre_neural_downscale_preset, self.pre_neural_downscale_custom):
            _pre_neural_var.trace_add("write", lambda *_: self._refresh_native_sr_scale_plan())
            _pre_neural_var.trace_add("write", lambda *_: self._guarded_section2_refresh_preview())
        for _sr_scale_var in (self.native_sr_preseed_preset, self.native_sr_preseed_custom):
            _sr_scale_var.trace_add("write", lambda *_: self._refresh_native_sr_scale_plan())
            _sr_scale_var.trace_add("write", lambda *_: self._guarded_section2_refresh_preview())
        self.native_sr_enable.trace_add("write", lambda *_: self._guarded_section2_refresh_preview())
        self.seed_target_resolution.trace_add("write", lambda *_: self._guarded_section2_update_upscale_controls())
        self.upscale_engine.trace_add("write", lambda *_: self._guarded_section2_update_upscale_controls())
        for _seed_var in (self.seed_parameter_mode, self.seed_batch_max, self.seed_temporal_overlap,
                          self.seed_vae_tile, self.seed_vae_spatial_overlap):
            _seed_var.trace_add("write", lambda *_: self._guarded_section2_refresh_preview())

    def _section2_sync_in_progress(self) -> bool:
        return bool(getattr(self, "_section2_syncing_selection", False))

    def _guarded_section2_refresh_preview(self) -> None:
        if self._section2_sync_in_progress():
            return
        pending = getattr(self, "_light_preview_after_id", None)
        if pending:
            try:
                self.after_cancel(pending)
            except Exception:
                pass
        self._light_preview_after_id = self.after(1, self._run_light_preview_refresh)

    def _run_light_preview_refresh(self) -> None:
        self._light_preview_after_id = None
        try:
            self._refresh_preview()
        except BackendError as exc:
            if hasattr(self, "geometry_preview"):
                self.geometry_preview.set(f"Invalid scaling configuration: {exc}")

    def _guarded_section2_update_encode_controls(self) -> None:
        if self._section2_sync_in_progress():
            return
        self._update_encode_controls()

    def _guarded_section2_update_rife_controls(self) -> None:
        if self._section2_sync_in_progress():
            return
        self._update_rife_controls()

    def _guarded_section2_update_fps_reduce_controls(self) -> None:
        if self._section2_sync_in_progress():
            return
        self._update_fps_reduce_controls()

    def _guarded_section2_update_upscale_controls(self) -> None:
        if self._section2_sync_in_progress():
            return
        self._update_upscale_controls()

    def _build_ui(self):
        outer = ttk.Frame(self, padding=10)
        outer.pack(fill="both", expand=True)

        head = ttk.Frame(outer)
        head.pack(fill="x", pady=(0, 8))
        ttk.Label(head, text=APP_NAME, style="Header.TLabel").pack(side="left")
        ttk.Label(head, text="SeedVR2 • four-stage Upscaling • RIFE • NVENC", style="Sub.TLabel").pack(side="left", padx=(16, 0), pady=(7, 0))


        box = ttk.LabelFrame(outer, text="1. Input / Queue", style="Blue.TLabelframe", padding=8)
        box.pack(fill="x", pady=(0, 8))
        r = ttk.Frame(box, style="Blue.TFrame")
        r.pack(fill="x")

        ttk.Radiobutton(
            r,
            text="One video",
            variable=self.input_mode,
            value="file",
            style="Blue.TRadiobutton",
            command=self._update_controls,
        ).pack(side="left")
        ttk.Radiobutton(
            r,
            text="Folder of videos",
            variable=self.input_mode,
            value="folder",
            style="Blue.TRadiobutton",
            command=self._update_controls,
        ).pack(side="left", padx=(8, 0))
        self.rec_check = ttk.Checkbutton(
            r,
            text="Include subfolders",
            variable=self.recursive,
            style="Blue.TCheckbutton",
        )
        self.rec_check.pack(side="left", padx=(8, 0))
        self.input_entry = ttk.Entry(r, textvariable=self.input_path, width=31)
        self.input_entry.pack(side="left", padx=(6, 3))
        self.input_entry.bind("<Return>", lambda _e: self._scan_input())
        ttk.Button(r, text="Browse...", command=self._browse_input).pack(side="left")

        ttk.Label(r, text="— Output is automatic: first movie folder\\VideoUpscaled", style="Blue.TLabel").pack(side="left", padx=8)

        r2 = ttk.Frame(box, style="Blue.TFrame")
        r2.pack(fill="x", pady=(7, 0))

        ttk.Checkbutton(
            r2,
            text="Move source movies",
            variable=self.move_processed_enable,
            style="Blue.TCheckbutton",
            command=self._update_move_processed_controls,
        ).pack(side="left")
        ttk.Label(r2, text="Success subfolder:", style="Blue.TLabel").pack(side="left", padx=(8, 2))
        self.move_success_entry = ttk.Entry(r2, textvariable=self.move_success_folder, width=22)
        self.move_success_entry.pack(side="left")
        self.move_success_browse = ttk.Button(r2, text="Browse...", command=self._browse_move_success_folder)
        self.move_success_browse.pack(side="left", padx=(3, 0))
        ttk.Label(r2, text="Failed subfolder:", style="Blue.TLabel").pack(side="left", padx=(8, 2))
        self.move_failed_entry = ttk.Entry(r2, textvariable=self.move_failed_folder, width=22)
        self.move_failed_entry.pack(side="left")
        self.move_failed_browse = ttk.Button(r2, text="Browse...", command=self._browse_move_failed_folder)
        self.move_failed_browse.pack(side="left", padx=(3, 0))

        r3 = ttk.Frame(box, style="Blue.TFrame")
        r3.pack(fill="x", pady=(6, 0))
        self.dynamic_paths_text = tk.StringVar(
            value=(
                f"Dynamic folders: <first movie folder>\\{DEFAULT_SUCCESS_FOLDER} | "
                f"<first movie folder>\\{DEFAULT_FAILED_FOLDER} | "
                f"<first movie folder>\\{DEFAULT_OUTPUT_FOLDER}"
            )
        )
        ttk.Label(
            r3,
            textvariable=self.dynamic_paths_text,
            style="Blue.TLabel",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

        ttk.Label(
            r3,
            textvariable=self.temp_space_prediction,
            style="Blue.TLabel",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", padx=(18, 0))

        qf = ttk.Frame(box, style="Blue.TFrame")
        qf.pack(fill="both", expand=True, pady=(7, 0))

        qtable = ttk.Frame(qf, style="Blue.TFrame")
        qtable.pack(fill="both", expand=True)
        qtable.rowconfigure(0, weight=1)
        qtable.columnconfigure(0, weight=1)

        cols = (
            "order", "file", "engine", "factor", "source", "output_resolution", "fps_input",
            "fps_ai", "fps_output", "bitrate", "duration",
            "similarity", "prediction_evidence", "estimated", "elapsed", "eta", "progress"
        )
        self.tree = ttk.Treeview(qtable, columns=cols, show="headings", height=7, selectmode="extended")
        titles = {
            "order": "Order",
            "file": "File",
            "engine": "Engine",
            "factor": "Factor",
            "source": "Source resolution",
            "output_resolution": "Output resolution",
            "fps_input": "FPS Input",
            "fps_ai": "FPS for AI",
            "fps_output": "FPS Output",
            "bitrate": "Pred. bitrate",
            "duration": "Movie length",
            "similarity": "Config. similarity",
            "prediction_evidence": "Prediction evidence",
            "estimated": "Processing time",
            "elapsed": "Time spent",
            "eta": "ETA",
            "progress": "Progress",
        }
        widths = {
            "order": 58,
            "file": 190,
            "engine": 92,
            "factor": 145,
            "source": 98,
            "output_resolution": 110,
            "fps_input": 72,
            "fps_ai": 76,
            "fps_output": 76,
            "bitrate": 88,
            "duration": 82,
            "similarity": 120,
            "prediction_evidence": 170,
            "estimated": 102,
            "elapsed": 82,
            "eta": 68,
            "progress": 190,
        }

        self.queue_columns = tuple(cols)
        self._tree_titles = dict(titles)
        self._tree_sort_column = "order"
        self._tree_sort_reverse = False
        self._order_editor = None
        self._factor_overlays: Dict[str, tk.Label] = {}

        for c in cols:
            self.tree.heading(
                c,
                text=titles[c],
                command=lambda col=c: self._sort_queue_table(col),
            )
            self.tree.column(
                c,
                width=widths[c],
                anchor="w" if c in ("file", "progress") else "center",
            )


        self.tree.bind("<Double-1>", self._queue_double_click_view_only)
        self.tree.bind("<ButtonRelease-1>", self._queue_single_click_order_edit, add="+")
        self.tree.bind("<<TreeviewSelect>>", self._on_queue_selection_changed, add="+")
        self.tree.bind("<Configure>", lambda _e: self.after_idle(self._refresh_factor_overlays), add="+")
        self.tree.bind("<MouseWheel>", lambda _e: self.after_idle(self._refresh_factor_overlays), add="+")
        self.tree.bind("<ButtonRelease-1>", lambda _e: self.after_idle(self._refresh_factor_overlays), add="+")
        def queue_yview(*args):
            self.tree.yview(*args)
            self.after_idle(self._refresh_factor_overlays)

        def queue_xview(*args):
            self.tree.xview(*args)
            self.after_idle(self._refresh_factor_overlays)

        ys = ttk.Scrollbar(qtable, orient="vertical", command=queue_yview)
        xs = ttk.Scrollbar(qtable, orient="horizontal", command=queue_xview)
        self.tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")

        qb = ttk.Frame(box, style="Blue.TFrame")
        qb.pack(fill="x", pady=(6, 0))
        ttk.Button(qb, text="Select All", command=self._select_all_queue).pack(side="left")
        ttk.Button(qb, text="Select None", command=self._select_none_queue).pack(side="left", padx=(6, 0))
        ttk.Button(qb, text="Remove selected", command=self._remove_selected).pack(side="left", padx=(12, 0))
        self.delete_selected_movies_btn = tk.Button(
            qb,
            text="DELETE selected movies",
            command=self._delete_selected_movies,
            bg="#B3261E",
            fg="white",
            activebackground="#8C1D18",
            activeforeground="white",
            disabledforeground="#E8C7C5",
            font=("Segoe UI", 9, "bold"),
            relief="raised",
            bd=2,
            padx=10,
            pady=2,
        )
        self.delete_selected_movies_btn.pack(side="left", padx=(6, 0))
        ttk.Button(qb, text="Clear queue", command=self._clear_queue).pack(side="left", padx=(6, 0))
        ttk.Label(
            qb,
            text="Table #1 is selection/display only. Select one or multiple rows (Ctrl/Shift); every change in Section #2 is applied immediately to the selected file(s). Double-click File to play. Click headers to sort.",
            style="Blue.TLabel",
        ).pack(side="left", padx=(18, 0))

        self.total_queue_estimate_text = tk.StringVar(value="Total queue estimated time: --")
        qsummary = ttk.Frame(box, style="Blue.TFrame")
        qsummary.pack(fill="x", pady=(5, 0))
        ttk.Label(
            qsummary,
            textvariable=self.total_queue_estimate_text,
            style="Blue.TLabel",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")


        settings_box = ttk.LabelFrame(outer, text="2. Settings for selected file(s) in Table #1", style="Purple.TLabelframe", padding=4)
        settings_box.pack(fill="x", pady=(0, 8))


        settings_box.configure(height=415)
        settings_box.pack_propagate(False)

        self.section2_selection_text = tk.StringVar(
            value="Select one or more files in Table #1. Section #2 is disabled until a row is selected."
        )
        ttk.Label(
            settings_box,
            textvariable=self.section2_selection_text,
            style="Purple.TLabel",
            font=("Segoe UI", 9, "bold"),
        ).pack(fill="x", padx=3, pady=(0, 5))

        nb = ttk.Notebook(settings_box, style="Pastel.TNotebook")
        nb.pack(fill="both", expand=True)
        self.settings_nb = nb
        t_fps = ttk.Frame(nb, padding=9)
        t_enhancement = ttk.Frame(nb, padding=9)
        t_preseed = ttk.Frame(nb, padding=9)
        t_upscale = ttk.Frame(nb, padding=9)
        t_sr = ttk.Frame(nb, padding=9)
        t_seed_advanced = ttk.Frame(nb, padding=9)
        t_rife = ttk.Frame(nb, padding=9)
        t_enc = ttk.Frame(nb, padding=9)
        t_tools = ttk.Frame(nb, padding=9)
        t_files = ttk.Frame(nb, padding=9)
        nb.add(t_fps, text="FPS Reduce")
        nb.add(t_enhancement, text="Enhancement")
        nb.add(t_preseed, text="Upscaling")
        nb.add(t_seed_advanced, text="SeedVR2 Advanced")
        nb.add(t_rife, text="RIFE")
        nb.add(t_enc, text="Encoding")
        nb.add(t_tools, text="Tools / ComfyUI")
        nb.add(t_files, text="Files / VSR Advanced")
        self.settings_tabs = {
            "FPS Reduce": t_fps,
            "Enhancement": t_enhancement,
            "Upscaling": t_preseed,
            "SeedVR2 Advanced": t_seed_advanced,
            "VSR Advanced": t_files,
            "Files / VSR Advanced": t_files,
            "RIFE": t_rife,
            "Encoding": t_enc,
            "Tools / ComfyUI": t_tools,
            "Files": t_files,
        }
        self._build_fps_reduce_tab(t_fps)
        self._build_enhancement_tab(t_enhancement)
        self._build_preseed_tab(t_preseed)
        merged = ttk.PanedWindow(t_files, orient="horizontal")
        merged.pack(fill="both", expand=True)
        files_panel = ttk.Frame(merged)
        vsr_panel = ttk.Frame(merged)
        self._files_global_panel = files_panel
        merged.add(files_panel, weight=3)
        merged.add(vsr_panel, weight=2)
        self._build_native_sr_tab(vsr_panel)
        self._build_seed_advanced_tab(t_seed_advanced)
        self._build_rife_tab(t_rife)
        self._build_encode_tab(t_enc)
        self._build_tools_tab(t_tools)
        self._build_files_tab(files_panel)
        self._capture_section2_widget_states()
        self._set_section2_enabled(False)


        pb = ttk.LabelFrame(outer, text="3. Processing", style="Green.TLabelframe", padding=8)
        pb.pack(fill="x", pady=(0, 8))
        br = ttk.Frame(pb, style="Green.TFrame")
        br.pack(fill="x")
        processing_button_width = 17
        self.start_highlight_frame = tk.Frame(br, bg=PASTEL["green"], bd=0, highlightthickness=0)
        self.start_highlight_frame.pack(side="left")
        self.start_btn = ttk.Button(self.start_highlight_frame, text="START QUEUE", style="Start.TButton", command=self._start_queue, width=processing_button_width)
        self.start_btn.pack(padx=10, pady=10)
        self.stop_btn = ttk.Button(br, text="STOP", style="Stop.TButton", command=self._stop_queue, state="disabled", width=processing_button_width)
        self.stop_btn.pack(side="left", padx=(8, 0))
        self.pause_highlight_frame = tk.Frame(br, bg=PASTEL["green"], bd=0, highlightthickness=0)
        self.pause_highlight_frame.pack(side="left", padx=(8, 0))
        self.pause_btn = ttk.Button(self.pause_highlight_frame, text="PAUSE", style="Pause.TButton", command=self._pause_queue, state="disabled", width=processing_button_width)
        self.pause_btn.pack(padx=10, pady=10)
        self.resume_btn = ttk.Button(br, text="RESUME", style="Resume.TButton", command=self._resume_queue, state="disabled", width=processing_button_width)
        self.resume_btn.pack(side="left", padx=(8, 0))
        # Legacy checkpoint-only SAVE & EXIT is removed. The invisible reference
        # keeps old pause/stop bookkeeping harmless during migration.
        self.save_exit_btn = ttk.Button(br, state="disabled")
        self.open_output_btn = ttk.Button(br, text="Output Folder", style="OpenOutput.TButton", command=self._open_output_folder, width=processing_button_width)
        self.open_output_btn.pack(side="left", padx=(8, 0))
        ttk.Label(br, textvariable=self.comfy_status_text, style="Green.TLabel").pack(side="right")


        meters = ttk.Frame(pb, style="Green.TFrame")
        meters.pack(fill="x", pady=(7, 0))
        for column in range(4):
            meters.columnconfigure(column, weight=1)

        cpu_box = ttk.Frame(meters, style="Green.TFrame")
        cpu_box.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Label(cpu_box, textvariable=self.cpu_usage_text, width=15, style="Green.TLabel").pack(side="left")
        ttk.Progressbar(cpu_box, variable=self.cpu_usage, maximum=100).pack(side="left", fill="x", expand=True)

        gpu_box = ttk.Frame(meters, style="Green.TFrame")
        gpu_box.grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Label(gpu_box, textvariable=self.gpu_usage_text, width=15, style="Green.TLabel").pack(side="left")
        ttk.Progressbar(gpu_box, variable=self.gpu_usage, maximum=100).pack(side="left", fill="x", expand=True)

        vram_box = ttk.Frame(meters, style="Green.TFrame")
        vram_box.grid(row=0, column=2, sticky="ew", padx=6)
        ttk.Label(vram_box, textvariable=self.vram_usage_text, width=22, style="Green.TLabel").pack(side="left")
        self.vram_bar = ttk.Progressbar(vram_box, variable=self.vram_usage, maximum=100)
        self.vram_bar.pack(side="left", fill="x", expand=True)

        spill_box = ttk.Frame(meters, style="Green.TFrame")
        spill_box.grid(row=0, column=3, sticky="ew", padx=(6, 0))
        self.vram_spill_label = ttk.Label(
            spill_box, textvariable=self.vram_spill_text, width=26, style="Spill.Normal.TLabel"
        )
        self.vram_spill_label.pack(side="left")
        self.vram_spill_bar = ttk.Progressbar(
            spill_box, variable=self.vram_spill_usage, maximum=100, style="Horizontal.TProgressbar"
        )
        self.vram_spill_bar.pack(side="left", fill="x", expand=True)

        p = ttk.Frame(pb, style="Green.TFrame")
        p.pack(fill="x", pady=(8, 0))
        ttk.Label(p, text="Overall", width=10, style="Green.TLabel").pack(side="left")
        ttk.Progressbar(p, variable=self.overall_progress, maximum=100).pack(side="left", fill="x", expand=True)
        p2 = ttk.Frame(pb, style="Green.TFrame")
        p2.pack(fill="x", pady=(4, 0))
        ttk.Label(p2, text="Current file", width=10, style="Green.TLabel").pack(side="left")
        ttk.Progressbar(p2, variable=self.file_progress, maximum=100).pack(side="left", fill="x", expand=True)
        ttk.Label(p2, textvariable=self.eta_text, width=20, style="Green.TLabel").pack(side="left", padx=(8, 0))
        p3 = ttk.Frame(pb, style="Green.TFrame")
        p3.pack(fill="x", pady=(5, 0))
        ttk.Label(p3, textvariable=self.current_file_text, style="Green.TLabel").pack(side="left")
        ttk.Label(p3, textvariable=self.current_step_text, style="Green.TLabel").pack(side="left", padx=(25, 0))
        ttk.Label(p3, textvariable=self.temp_path_text, style="Green.TLabel").pack(side="right")
        p4 = ttk.Frame(pb, style="Green.TFrame")
        p4.pack(fill="x", pady=(4, 0))

        ttk.Label(
            p4,
            textvariable=self.rife_status_text,
            style="Green.TLabel",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", padx=(24, 0))


        lb = ttk.LabelFrame(outer, text="4. Live log", style="Purple.TLabelframe", padding=6)
        lb.pack(fill="both", expand=True)
        logbar = ttk.Frame(lb, style="Purple.TFrame")
        logbar.pack(fill="x", pady=(0, 4))
        ttk.Button(logbar, text="Clear Live Log", command=self._clear_live_log).pack(side="right")
        self.log = ScrolledText(lb, height=12, font=("Consolas", 9), wrap="word", bg="#FBFAFE", fg=PASTEL["text"])
        self.log.pack(fill="both", expand=True)
        self.log.configure(state="disabled")

    def _build_fps_reduce_tab(self, p):
        b = ttk.LabelFrame(
            p,
            text="FPS reduction before AI upscaling",
            style="Blue.TLabelframe",
            padding=8,
        )
        b.pack(fill="x")

        ttk.Checkbutton(
            b,
            text="Enable FPS reduction before denoise / AI",
            variable=self.fps_reduce_enable,
            style="Blue.TCheckbutton",
        ).grid(row=0, column=0, columnspan=4, sticky="w")

        self.fps_reduce_max_label = ttk.Label(
            b,
            text="FPS Max for AI:",
            style="Blue.TLabel",
            font=("Segoe UI", 10, "bold"),
        )
        self.fps_reduce_max_label.grid(row=1, column=0, sticky="w", pady=(8, 0))

        self.fps_reduce_max_box = ttk.Combobox(
            b,
            textvariable=self.fps_reduce_max,
            values=[str(x) for x in FPS_MAX_FOR_AI_CHOICES],
            state="readonly",
            width=8,
        )
        self.fps_reduce_max_box.grid(
            row=1, column=1, sticky="w", padx=(8, 18), pady=(8, 0)
        )

        ttk.Label(
            b,
            textvariable=self.fps_reduce_preview,
            style="Blue.TLabel",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))

        self._update_fps_reduce_controls()

    def _update_fps_reduce_controls(self) -> None:
        if not hasattr(self, "fps_reduce_max_box"):
            return

        enabled = bool(self._raw_tk_value(self.fps_reduce_enable))

        self.fps_reduce_max_box.configure(
            state="readonly" if enabled else "disabled"
        )
        if hasattr(self, "fps_reduce_max_label"):
            self.fps_reduce_max_label.state(
                ["!disabled"] if enabled else ["disabled"]
            )

    def _build_repair_tab(self, p):
        b = ttk.LabelFrame(
            p,
            text="Automatic video repair",
            style="Yellow.TLabelframe",
            padding=8,
        )
        b.pack(fill="x")
        ttk.Label(
            b,
            text="Automatic repair:",
            style="Yellow.TLabel",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(
            b,
            text="On",
            variable=self.repair_enable,
            value=True,
            style="Yellow.TRadiobutton",
        ).grid(row=0, column=1, sticky="w", padx=(12, 4))
        ttk.Radiobutton(
            b,
            text="Off",
            variable=self.repair_enable,
            value=False,
            style="Yellow.TRadiobutton",
        ).grid(row=0, column=2, sticky="w", padx=4)

    def _build_enhancement_tab(self, p):
        master = ttk.Frame(p)
        master.pack(fill="x", pady=(0, 5))
        self.enhancement_toggle_button = tk.Button(
            master, text="ENHANCEMENT ON", width=23, padx=8, pady=5,
            font=("Segoe UI", 10, "bold"), relief="raised", bd=2,
            command=self._toggle_enhancement_enable)
        self.enhancement_toggle_button.pack(side="left")
        ttk.Label(master, text="OFF bypasses Repair, Deinterlace, Denoise and image corrections; FPS Reduce remains independent.",
                  foreground="#667085").pack(side="left", padx=12)

        repair_area = ttk.Frame(p)
        repair_area.pack(fill="x", pady=(0, 6))
        self._build_repair_tab(repair_area)

        b = ttk.LabelFrame(
            p,
            text="Automatic enhancement / final detail",
            style="Peach.TLabelframe",
            padding=8,
        )
        b.pack(fill="x")
        for col in (1, 4):
            b.columnconfigure(col, weight=1)

        left_rows = [
            ("Denoise", self.denoise),
            ("Color", self.color_correction),
            ("Brightness", self.brightness_correction),
        ]
        right_rows = [
            ("White balance", self.white_correction),
        ]

        for row, (label, var) in enumerate(left_rows):
            ttk.Label(
                b,
                text=label + ":",
                style="Peach.TLabel",
                font=("Segoe UI", 10, "bold"),
                width=17,
            ).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Checkbutton(
                b,
                text="On (Auto)",
                variable=var,
                onvalue="Auto",
                offvalue="Off",
                style="Peach.TCheckbutton",
            ).grid(row=row, column=1, sticky="w", padx=(8, 28), pady=4)

        for row, (label, var) in enumerate(right_rows):
            ttk.Label(
                b,
                text=label + ":",
                style="Peach.TLabel",
                font=("Segoe UI", 10, "bold"),
                width=17,
            ).grid(row=row, column=3, sticky="w", pady=4)
            ttk.Checkbutton(
                b,
                text="On (Auto)",
                variable=var,
                onvalue="Auto",
                offvalue="Off",
                style="Peach.TCheckbutton",
            ).grid(row=row, column=4, sticky="w", padx=(8, 14), pady=4)

        ttk.Label(
            b, text="Sharpen:", style="Peach.TLabel",
            font=("Segoe UI", 10, "bold"), width=17
        ).grid(row=1, column=3, sticky="w", pady=4)
        ttk.Combobox(
            b, textvariable=self.sharpen,
            values=["Off", "Auto", "Low", "Medium", "High"],
            state="readonly", width=14
        ).grid(row=1, column=4, sticky="w", padx=(8, 14), pady=4)

        ttk.Label(
            b, text="Deband:", style="Peach.TLabel",
            font=("Segoe UI", 10, "bold"), width=17
        ).grid(row=2, column=3, sticky="w", pady=4)
        ttk.Combobox(
            b, textvariable=self.deband,
            values=["Off", "Low", "Medium", "High"],
            state="readonly", width=14
        ).grid(row=2, column=4, sticky="w", padx=(8, 14), pady=4)

        ttk.Label(
            b,
            text="Deinterlace (Auto):",
            style="Peach.TLabel",
            font=("Segoe UI", 10, "bold"),
            width=19,
        ).grid(row=3, column=0, sticky="w", pady=4)
        deinterlace_choices = ttk.Frame(b, style="Peach.TFrame")
        deinterlace_choices.grid(row=3, column=1, sticky="w", padx=(8, 28), pady=4)
        ttk.Radiobutton(
            deinterlace_choices,
            text="Yes",
            variable=self.deinterlace_auto,
            value=True,
            style="Peach.TRadiobutton",
        ).pack(side="left")
        ttk.Radiobutton(
            deinterlace_choices,
            text="No",
            variable=self.deinterlace_auto,
            value=False,
            style="Peach.TRadiobutton",
        ).pack(side="left", padx=(12, 0))

        ttk.Separator(b, orient="vertical").grid(row=0, column=2, rowspan=4, sticky="ns", padx=16)

        ttk.Label(
            b,
            text=(
                ""
                ""
                ""
                ""
                ""
            ),
            style="Peach.TLabel", wraplength=1120, justify="left"
        ).grid(row=4, column=0, columnspan=5, sticky="w", pady=(8, 0))

        self.enhancement_control_widgets = []
        for panel in (repair_area, b):
            self.enhancement_control_widgets.extend(self._iter_widget_descendants(panel))
        self._update_enhancement_controls()

    def _enhancement_is_enabled(self) -> bool:
        return bool(self._job_setting("enhancement_enable", self.enhancement_enable))

    def _toggle_enhancement_enable(self) -> None:
        self.enhancement_enable.set(not bool(self._raw_tk_value(self.enhancement_enable)))
        self._update_enhancement_controls()
        self._guarded_section2_refresh_preview()

    def _update_enhancement_controls(self) -> None:
        if not hasattr(self, "enhancement_toggle_button"):
            return
        enabled = bool(self._raw_tk_value(self.enhancement_enable))
        self.enhancement_toggle_button.configure(
            text="ENHANCEMENT ON" if enabled else "ENHANCEMENT OFF",
            bg="#2E8B57" if enabled else "#D9D9D9",
            fg="white" if enabled else "#555555")
        # The master switch remains usable. Every embedded Repair/Enhancement
        # option is unavailable while OFF, without changing its saved value.
        # Section 2 must also remain disabled when no video row is selected.
        active = enabled and bool(self._selected_jobs_from_table())
        for widget in getattr(self, "enhancement_control_widgets", ()):
            try:
                widget.configure(state="normal" if active else "disabled")
            except (tk.TclError, AttributeError):
                try:
                    widget.state(["!disabled"] if active else ["disabled"])
                except (tk.TclError, AttributeError):
                    pass

    def _build_preseed_tab(self, p):
        outer = ttk.Frame(p)
        outer.pack(fill="both", expand=True)
        methods = ("Bicubic", "BasicVSR++ 4X (Blurry)", "RealBasicVSR 4X (Landscape)", "SeedVR2 restoration")
        bar = ttk.Frame(outer)
        bar.pack(fill="x", pady=(0, 9))
        self.scaling_toggle_button = tk.Button(
            bar, text="UPSCALING ON", width=22, padx=8, pady=5,
            font=("Segoe UI", 10, "bold"), relief="raised", bd=2,
            command=self._toggle_scaling_enable)
        self.scaling_toggle_button.pack(side="left")
        ttk.Label(bar, text="Master OFF bypasses all four stages. Each stage also has an independent ON/OFF switch.",
                  foreground="#667085").pack(side="left", padx=10)
        stages_row = ttk.Frame(outer)
        stages_row.pack(fill="x", pady=(0, 8))
        for i in range(4):
            stages_row.columnconfigure(i, weight=1, uniform="scaling")
        self.scaling_boxes = []
        self.scaling_stage_toggle_buttons = []
        for index in (1, 2, 3, 4):
            order = ("first", "second", "third", "fourth")[index - 1]
            group = ttk.LabelFrame(stages_row, text=f"Scaling {index} (applied {order})", style="Blue.TLabelframe", padding=7)
            group.grid(row=0, column=index-1, sticky="nsew", padx=(0 if index == 1 else 5, 0 if index == 4 else 5))
            group.columnconfigure(1, weight=1)
            enabled_var = getattr(self, f"scaling{index}_enabled")
            mode_var = getattr(self, f"scaling{index}_method")
            factor_var = getattr(self, f"scaling{index}_factor")
            target_var = getattr(self, f"scaling{index}_target")
            toggle = tk.Button(group, text=f"STAGE {index} ON", width=19, padx=4, pady=4,
                               font=("Segoe UI", 9, "bold"), relief="raised", bd=2,
                               command=lambda n=index: self._toggle_scaling_stage(n))
            toggle.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 7))
            self.scaling_stage_toggle_buttons.append(toggle)
            ttk.Label(group, text="Method:", style="Blue.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=3)
            mode = ttk.Combobox(group, textvariable=mode_var, values=methods, state="readonly", width=27)
            mode.grid(row=1, column=1, sticky="ew", pady=3)
            ttk.Label(group, text="Scale factor:", style="Blue.TLabel").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=3)
            factor = ttk.Combobox(group, textvariable=factor_var,
                                  values=[f"{i * 0.05:.2f}X" for i in range(2, 201)],
                                  width=15, state="readonly")
            factor.grid(row=2, column=1, sticky="w", pady=3)
            ttk.Label(group, text="Target resolution:", style="Blue.TLabel").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=3)
            target = ttk.Combobox(group, textvariable=target_var,
                                  values=["Factor", "480p", "720p", "1080p", "1440p", "2160p"],
                                  width=15, state="readonly")
            target.grid(row=3, column=1, sticky="w", pady=3)
            ttk.Label(group,
                      text="",
                      style="Blue.TLabel", wraplength=260, justify="left").grid(row=4, column=0, columnspan=2, sticky="w", pady=(6,0))
            self.scaling_boxes.append((mode, factor, target))
            mode.bind("<<ComboboxSelected>>", lambda _e, n=index: self._scaling_method_changed(n))
            factor.bind("<<ComboboxSelected>>", lambda _e, n=index: self._scaling_factor_changed(n))
            target.bind("<<ComboboxSelected>>", lambda _e, n=index: self._scaling_target_changed(n))
        summary = ttk.LabelFrame(outer, text="Combined four-stage output / Processing order", style="Green.TLabelframe", padding=8)
        summary.pack(fill="x")
        ttk.Label(summary, textvariable=self.native_sr_scale_plan, style="Green.TLabel",
                  font=("Segoe UI", 10, "bold"), wraplength=1200, justify="left").pack(anchor="w")
        self._update_scaling_widgets()
        self._refresh_native_sr_scale_plan()

    def _toggle_scaling_stage(self, index: int) -> None:
        variable = getattr(self, f"scaling{index}_enabled")
        variable.set(not bool(self._raw_tk_value(variable)))
        self._update_scaling_widgets()
        self._refresh_native_sr_scale_plan()
        self._guarded_section2_refresh_preview()

    def _toggle_scaling_enable(self) -> None:
        self.scaling_enable.set(not bool(self._raw_tk_value(self.scaling_enable)))
        self._update_scaling_widgets()
        self._refresh_native_sr_scale_plan()
        self._guarded_section2_refresh_preview()

    def _scaling_method_changed(self, index: int) -> None:
        if self._section2_sync_in_progress():
            return
        name = getattr(self, f"scaling{index}_method").get()
        if name != "Bicubic":
            getattr(self, f"scaling{index}_factor").set("1.00X" if name == "SeedVR2 restoration" else "4.00X")
            getattr(self, f"scaling{index}_target").set("Factor")
        self._update_scaling_widgets()
        self._refresh_native_sr_scale_plan()
        self._guarded_section2_refresh_preview()

    def _scaling_factor_changed(self, index: int) -> None:
        if self._section2_sync_in_progress():
            return
        getattr(self, f"scaling{index}_target").set("Factor")
        self._refresh_native_sr_scale_plan()
        self._guarded_section2_refresh_preview()

    def _scaling_target_changed(self, index: int) -> None:
        if self._section2_sync_in_progress():
            return
        self._refresh_native_sr_scale_plan()
        self._guarded_section2_refresh_preview()

    def _update_scaling_widgets(self) -> None:
        master = bool(self._raw_tk_value(self.scaling_enable))
        if hasattr(self, "scaling_toggle_button"):
            self.scaling_toggle_button.configure(text="UPSCALING ON" if master else "UPSCALING OFF",
                                                 bg="#2E8B57" if master else "#D9D9D9",
                                                 fg="white" if master else "#555555")
        has_selected = bool(self._selected_jobs_from_table()) if hasattr(self, "tree") else True
        for n, (method_box, factor_box, target_box) in enumerate(getattr(self, "scaling_boxes", ()), start=1):
            enabled = bool(self._raw_tk_value(getattr(self, f"scaling{n}_enabled")))
            active = master and enabled and has_selected
            name = getattr(self, f"scaling{n}_method").get()
            if name != "Bicubic" and master:
                forced = "1.00X" if name == "SeedVR2 restoration" else "4.00X"
                if getattr(self, f"scaling{n}_factor").get() != forced:
                    getattr(self, f"scaling{n}_factor").set(forced)
                if getattr(self, f"scaling{n}_target").get() != "Factor":
                    getattr(self, f"scaling{n}_target").set("Factor")
            method_box.configure(state="readonly" if active else "disabled")
            factor_box.configure(state="readonly" if active and name == "Bicubic" else "disabled")
            target_box.configure(state="readonly" if active and name == "Bicubic" else "disabled")
            if n <= len(getattr(self, "scaling_stage_toggle_buttons", ())) :
                button = self.scaling_stage_toggle_buttons[n-1]
                button.configure(text=f"STAGE {n} {'ON' if enabled else 'OFF'}",
                                 bg="#2E8B57" if enabled and master else "#D9D9D9",
                                 fg="white" if enabled and master else "#555555",
                                 state="normal" if master and has_selected else "disabled")

    def _scaling_stage_plan(self, index: int, width: int, height: int) -> Tuple[str, float, int, int]:
        if width < 2 or height < 2:
            raise BackendError("Upscaling requires known source width and height.")
        if not bool(self._job_setting(f"scaling{index}_enabled", getattr(self, f"scaling{index}_enabled"))):
            return "OFF", 1.0, width, height
        mode = str(self._job_setting(f"scaling{index}_method", getattr(self, f"scaling{index}_method")))
        if mode not in ("Bicubic", "BasicVSR++ 4X (Blurry)", "RealBasicVSR 4X (Landscape)", "SeedVR2 restoration"):
            raise BackendError(f"Scaling {index}: unknown method {mode!r}.")
        target = str(self._job_setting(f"scaling{index}_target", getattr(self, f"scaling{index}_target")))
        if mode == "SeedVR2 restoration":
            scale = 1.0
        elif mode != "Bicubic":
            scale = 4.0
        elif target in TARGET_HEIGHTS:
            scale = TARGET_HEIGHTS[target] / float(height)
        else:
            raw = str(self._job_setting(f"scaling{index}_factor", getattr(self, f"scaling{index}_factor")))
            try:
                scale = float(raw.strip().rstrip("Xx").replace(",", "."))
            except (ValueError, OverflowError):
                raise BackendError(f"Scaling {index}: invalid factor {raw!r}.")
            if not math.isfinite(scale) or not 0.10 <= scale <= 10.0:
                raise BackendError(f"Scaling {index}: factor must be 0.10X–10.00X.")
        output_width = self._even_dimension(width * scale)
        output_height = self._even_dimension(height * scale)
        if mode.startswith(("BasicVSR++", "RealBasicVSR")):
            output_width, output_height = width * 4, height * 4
        if mode == "SeedVR2 restoration":
            output_width, output_height = width, height
        if min(output_width, output_height) < 2 or max(output_width, output_height) > 8192:
            raise BackendError(f"Scaling {index}: output {output_width}x{output_height} exceeds permitted 2–8192px dimensions.")
        return mode, scale, output_width, output_height

    def _four_scaling_plan(self, info: VideoInfo) -> Tuple[List[Tuple[str, float, int, int]], int, int]:
        width, height = int(info.width), int(info.height)
        if not bool(self._job_setting("scaling_enable", self.scaling_enable)):
            # Explicit bypass entries preserve geometry in preview and ETA calculations.
            return [("OFF", 1.0, width, height) for _ in range(4)], width, height
        plan = []
        for index in (1, 2, 3, 4):
            item = self._scaling_stage_plan(index, width, height)
            plan.append(item)
            width, height = item[2], item[3]
        return plan, width, height

    def _run_four_scaling_stages(self, job: Job, source: Path, temp_dir: Path) -> Path:
        working = Path(source)
        if not bool(self._job_setting("scaling_enable", self.scaling_enable)):
            self._post("log", "V264 UPSCALING OFF: all four stages bypassed.")
            return working
        initial = self._probe_video(working)
        for index in (1, 2, 3, 4):
            info = self._probe_video(working)
            mode, multiplier, target_w, target_h = self._scaling_stage_plan(index, info.width, info.height)
            self._post("log", f"V265 STAGE {index}/4: {mode}; {info.width}x{info.height} -> {target_w}x{target_h}; factor {multiplier:g}X")
            if mode == "OFF" or (mode == "Bicubic" and (info.width, info.height) == (target_w, target_h)):
                continue
            stage_dir = Path(temp_dir) / f"scaling_{index}"
            stage_dir.mkdir(parents=True, exist_ok=True)
            begin = self._job_elapsed_now(job)
            self._set_stage(job, f"Scaling {index}/4: {mode}", 0.0, 0.25 + (index-1)*0.10, 0.10)
            if mode == "Bicubic":
                output = stage_dir / f"bicubic_{index}_lossless.mkv"

                command = [self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "error", "-i", str(working),
                           "-map", "0:v:0", "-an", "-sn", "-vf", f"scale={target_w}:{target_h}:flags=bicubic",
                           "-c:v", "ffv1", "-level", "3", "-pix_fmt", "gbrp",
                           "-fps_mode:v", "passthrough", str(output)]
                if self._run_process(command, job) != 0 or not output.is_file():
                    raise BackendError(f"Scaling {index}: bicubic FFV1 failed; see log.")
                job.stage_preseed_resize_seconds += max(0.0, self._job_elapsed_now(job) - begin)
            elif mode == "SeedVR2 restoration":
                output = self._run_seedvr2_scaling_stage(job, working, stage_dir, index, info)
            else:
                model = "BasicVSRPlusPlus_x4" if mode.startswith("BasicVSR++") else "RealBasicVSR_x4"
                output = self._run_native_neural_sr(job, working, stage_dir, 4, requested_factor=4.0, model_override=model)
            check = self._probe_video(output)
            if (check.width, check.height) != (target_w, target_h):
                raise BackendError(f"Scaling {index}: verified {check.width}x{check.height}; expected {target_w}x{target_h}.")

            if info.frames and check.frames and info.frames != check.frames:
                self._post("log", f"V266 SCALING {index} FRAME AUDIT: metadata reports "
                                  f"input={info.frames}, output={check.frames}; "
                                  "counting actual decoded frames before accepting/rejecting.")
                actual_in = self._count_video_frames_exact(working, strict=True)
                actual_out = self._count_video_frames_exact(output, strict=True)
                self._post("log", f"V266 SCALING {index} FRAME AUDIT: "
                                  f"decoded input={actual_in}, decoded output={actual_out}.")
                if actual_in != actual_out:
                    raise BackendError(
                        f"Scaling {index}: REAL frame-count mismatch: decoded input "
                        f"{actual_in}, decoded output {actual_out}. "
                        "Output preserved for inspection; never invent or drop frames to pass verification."
                    )
                self._post("log", f"V266 SCALING {index}: metadata-only frame-count "
                                  "discrepancy; no frames were lost or duplicated.")
            if abs(info.fps - check.fps) > 0.02:
                raise BackendError(f"Scaling {index}: FPS changed from {info.fps:g} to {check.fps:g}.")
            self._post("log", f"V265 STAGE {index}/4 COMPLETE: {check.width}x{check.height} @ {check.fps:g} FPS; {check.frames} frames")
            working = Path(output)
            self._set_stage_fraction(job, 1.0)
        final = self._probe_video(working)
        plan, expected_w, expected_h = self._four_scaling_plan(initial)
        if (final.width, final.height) != (expected_w, expected_h):
            raise BackendError(f"Four-stage scaling was inconsistent: {final.width}x{final.height}; expected {expected_w}x{expected_h}.")
        return working

    def _run_seedvr2_scaling_stage(self, job: Job, source: Path, stage_dir: Path,
                                   index: int, input_info: VideoInfo) -> Path:
        """Run exactly one true SeedVR2 1X restoration pass at the selected stage."""
        previous_ai_info = job.ai_info
        job.ai_info = input_info
        preserved = False
        recovery_runtime_root = None
        try:
            self._post("log", f"V265 STAGE {index}/4: SeedVR2 1X restoration, {input_info.width}x{input_info.height}, no spatial enlargement.")
            started = self._job_elapsed_now(job)
            try:
                runtime_result = self._run_seedvr2(job, Path(source), 1.0, stage_dir)
            finally:
                job.stage_seedvr2_seconds += max(0.0, self._job_elapsed_now(job) - started)
            self._verify_seedvr2_output_geometry(job, runtime_result, 1.0)
            output = self._preserve_seedvr2_output_for_downstream(job, runtime_result, stage_dir, 1.0)
            preserved = True
            self._verify_seedvr2_output_geometry(job, output, 1.0)
            check = self._probe_video(Path(output))
            if (check.width, check.height) != (input_info.width, input_info.height):
                raise BackendError(f"Scaling {index}: SeedVR2 1X unexpectedly changed resolution.")
            return Path(output)
        finally:
            if self._comfy_runtime_root is not None:
                recovery_runtime_root = Path(self._comfy_runtime_root)
            self._stop_managed_comfy(
                reason=(f"V264 STAGE {index}: verified SeedVR2 output preserved; releasing VRAM."
                        if preserved else f"V264 STAGE {index}: SeedVR2 failed; keeping private recovery data."),
                wait_port=True)
            if preserved:
                self._cleanup_retained_comfy_inputs()
            else:
                if recovery_runtime_root is not None:
                    self._comfy_runtime_dirs_to_cleanup = [p for p in self._comfy_runtime_dirs_to_cleanup
                                                           if Path(p) != recovery_runtime_root]
                    kept = []
                    for p in self._comfy_retained_inputs:
                        try:
                            Path(p).relative_to(recovery_runtime_root)
                        except Exception:
                            kept.append(p)
                    self._comfy_retained_inputs = kept
                    self._post("log", f"V264 SeedVR2 recovery runtime preserved: {recovery_runtime_root}")
                self._cleanup_retained_comfy_inputs()
            job.ai_info = previous_ai_info

    def _pre_neural_preset_changed(self, _event=None) -> None:
        if not self._section2_sync_in_progress():
            self.pre_neural_downscale_custom.set("")
        self._refresh_native_sr_scale_plan()

    def _preseed_preset_changed(self, _event=None) -> None:
        if not self._section2_sync_in_progress():
            self.native_sr_preseed_custom.set("")
            self.preseed_resolution.set("Factor")
        self._refresh_native_sr_scale_plan()

    def _preseed_custom_changed(self) -> None:
        if not self._section2_sync_in_progress():
            if self.native_sr_preseed_custom.get().strip() and self.preseed_resolution.get() != "Factor":
                self.preseed_resolution.set("Factor")

    def _preseed_mode_changed(self) -> None:
        if self._section2_sync_in_progress():
            return
        mode = self.preseed_mode.get()
        if mode not in ("Only Bicubic", "BasicVSR++&Bicubic", "RealBasicVSR&Bicubic"):
            return
        neural = mode != "Only Bicubic"
        self.native_sr_enable.set(neural)
        if neural:
            self.seed_upscale.set("1X")
            model = "BasicVSRPlusPlus_x4" if mode.startswith("BasicVSR++") else "RealBasicVSR_x4"
            if self.native_sr_model.get() != model:
                self.native_sr_model.set(model)
                self._native_sr_select_model_defaults()
        if self.seed_target_resolution.get() != "Use upscale factor":
            self.seed_target_resolution.set("Use upscale factor")
        self._refresh_native_sr_scale_plan()
        self._guarded_section2_refresh_preview()

    def _selected_preseed_mode(self) -> str:
        return "Only Bicubic"


    def _selected_preseed_seed_factor(self, info: Optional[VideoInfo] = None) -> float:
        return 1.0


    def _preseed_target_dimensions(self, info: VideoInfo) -> Tuple[int, int, float]:
        _stages, w, h = self._four_scaling_plan(info)
        return w, h, w / max(1.0, info.width)


    def _run_preseed_bicubic(self, job: Job, source: Path, temp_dir: Path) -> Path:
        """Lossless, time-preserving bicubic resize for Only Bicubic mode."""
        info = self._probe_video(source)
        w, h, factor = self._preseed_target_dimensions(info)
        if (w, h) == (info.width, info.height):
            self._post("log", "V241 PRE-SEEDVR2 BICUBIC: 1X; source retained without re-encoding.")
            return source
        output = temp_dir / "preseed_bicubic_lossless.mkv"
        cmd = [self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "error",
               "-i", str(source), "-map", "0:v:0", "-an", "-sn",
               "-vf", f"scale={w}:{h}:flags=bicubic,format=gbrp",
               "-c:v", "ffv1", "-level", "3", "-pix_fmt", "gbrp",
               "-fps_mode", "passthrough", str(output)]
        self._post("log", f"V241 PRE-SEEDVR2 ONLY BICUBIC: {info.width}x{info.height} "
                          f"-> {w}x{h} ({factor:.5g}X); lossless FFV1.")
        if self._run_process(cmd, job) != 0 or not output.is_file() or output.stat().st_size < 1024:
            raise BackendError("Pre-SeedVR2 bicubic scaling failed; SeedVR2 was not started.")
        after = self._probe_video(output)
        if (after.width, after.height) != (w, h):
            raise BackendError(f"Bicubic frame geometry mismatch: {after.width}x{after.height} vs {w}x{h}.")
        if info.frames and after.frames and abs(after.frames-info.frames) > 1:
            raise BackendError(f"Bicubic frame count changed from {info.frames} to {after.frames}.")
        if abs(after.fps-info.fps) > .02:
            raise BackendError("Bicubic FPS changed unexpectedly.")
        return output

    def _build_downscale_tab(self, p):
        b = ttk.LabelFrame(p, text="Lanczos video downscaling", style="Blue.TLabelframe", padding=10)
        b.pack(fill="x")
        b.columnconfigure(1, weight=1)

        self.downscale_toggle_button = tk.Button(
            b, text="DOWNSCALE OFF", command=self._toggle_downscale_enable,
            width=24, bg="#D9D9D9", fg="#555555", font=("Segoe UI", 9, "bold"),
            relief="raised", bd=2,
        )
        self.downscale_toggle_button.grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Label(
            b, text="",
            style="Blue.TLabel", font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=1, columnspan=3, sticky="w", padx=(15, 0), pady=(0, 8))

        ttk.Label(b, text="Preset downscale factor:", style="Blue.TLabel").grid(row=1, column=0, sticky="w")
        self.downscale_preset_box = ttk.Combobox(
            b, textvariable=self.downscale_preset, values=DOWNSCALE_CHOICES,
            width=10, state="readonly",
        )
        self.downscale_preset_box.grid(row=1, column=1, sticky="w", padx=(8, 18))
        self.downscale_preset_box.bind("<<ComboboxSelected>>", self._downscale_preset_changed)

        ttk.Label(b, text="Custom factor (overrides preset):", style="Blue.TLabel").grid(row=1, column=2, sticky="e")
        self.downscale_custom_entry = ttk.Entry(b, textvariable=self.downscale_custom, width=14)
        self.downscale_custom_entry.grid(row=1, column=3, sticky="w", padx=(8, 0))

        ttk.Label(
            b, textvariable=self.downscale_preview, style="Blue.TLabel",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))
        ttk.Label(
            b, text=(
                ""
                ""
                ""
                ""
                ""
            ), style="Blue.TLabel", wraplength=1100, justify="left",
        ).grid(row=3, column=0, columnspan=4, sticky="w", pady=(10, 0))
        self._update_downscale_controls()

    def _downscale_preset_changed(self, _event=None) -> None:

        if not self._section2_sync_in_progress():
            self.downscale_custom.set("")
        self._update_downscale_controls()

    def _toggle_downscale_enable(self) -> None:
        self.downscale_enable.set(not bool(self._raw_tk_value(self.downscale_enable)))
        self._update_downscale_controls()

    def _selected_downscale_factor(self, strict: bool = False) -> float:
        custom = str(self._job_setting("downscale_custom", self.downscale_custom) or "").strip()
        preset = str(self._job_setting("downscale_preset", self.downscale_preset) or "0.75").strip()
        raw = custom if custom else preset
        try:
            factor = float(raw.replace(",", "."))
            if not math.isfinite(factor) or not (0.0 < factor < 1.0):
                raise ValueError("Factor must be strictly between 0 and 1.")
            return factor
        except (ValueError, OverflowError):
            if strict:
                raise BackendError(f"Invalid downscale factor '{raw}'. Enter a number > 0 and < 1 (for example 0.75).")
            return 0.75

    def _selected_downscale_enable(self) -> bool:

        return False

    def _downscale_dimensions(self, width: int, height: int) -> Tuple[int, int]:
        if not self._selected_downscale_enable() or width <= 0 or height <= 0:
            return int(width), int(height)
        factor = self._selected_downscale_factor()
        return self._even_dimension(width * factor), self._even_dimension(height * factor)

    def _update_downscale_controls(self) -> None:
        if not hasattr(self, "downscale_toggle_button"):
            return
        enabled = bool(self._raw_tk_value(self.downscale_enable))
        if enabled:
            self.downscale_toggle_button.configure(text="DOWNSCALE ON", bg="#2E8B57", fg="white")
        else:
            self.downscale_toggle_button.configure(text="DOWNSCALE OFF", bg="#D9D9D9", fg="#555555")
        self.downscale_preset_box.configure(state="readonly" if enabled else "disabled")
        self.downscale_custom_entry.configure(state="normal" if enabled else "disabled")
        jobs = self._selected_jobs_from_table() if hasattr(self, "tree") else []
        job = jobs[0] if jobs else (self.jobs[0] if self.jobs else None)
        if not enabled:
            self.downscale_preview.set("Downscale OFF — source resolution is unchanged by this tab.")
        elif job and job.info.width > 0 and job.info.height > 0:
            w, h = self._job_settings_call(job, self._downscale_dimensions, job.info.width, job.info.height)
            factor = self._job_settings_call(job, self._selected_downscale_factor)
            self.downscale_preview.set(
                f"Lanczos preview: {job.info.width}×{job.info.height} → {w}×{h} "
                f"({factor:g}×). "
                + ("Then AI Upscale." if self._job_settings_call(job, self._selected_upscale_enable)
                   else "Then final encode (no AI).")
            )
        else:
            self.downscale_preview.set(f"Lanczos factor {self._selected_downscale_factor():g}× — select a video to preview.")

    def _build_upscale_tab(self, p):
        box = ttk.LabelFrame(p, text="SeedVR2 restoration (no spatial enlargement)", style="Green.TLabelframe", padding=12)
        box.pack(fill="x")
        self.upscale_toggle_button = tk.Button(box, text="RESTORATION ON", command=self._toggle_upscale_enable,
            width=23, bg="#2E8B57", fg="white", font=("Segoe UI", 10, "bold"))
        self.upscale_toggle_button.pack(anchor="w", pady=8)
        ttk.Label(box, text="Scaling is configured exclusively in Up/Down Scaling. SeedVR2 runs at 1.00X on the result of scaling stages 1, 2 and 3; restoration does not change video dimensions.",
            style="Green.TLabel", wraplength=980, justify="left").pack(anchor="w", pady=4)
        ttk.Label(box, textvariable=self.geometry_preview, style="Green.TLabel", font=("Segoe UI", 10, "bold"), wraplength=980).pack(anchor="w", pady=8)
        self._update_upscale_controls()


    def _build_native_sr_tab(self, p):
        """V244: compact VSR setup beside the live, full-path file inventory."""
        b = ttk.LabelFrame(p, text="BasicVSR++ / RealBasicVSR setup", style="Green.TLabelframe", padding=6)
        b.pack(fill="both", expand=True, padx=(6, 0))
        b.columnconfigure(1, weight=1)
        ttk.Label(b, text="The neural method is chosen independently for Scaling 1, 2, 3 and 4:", style="Green.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w")
        model_summary = ttk.Frame(b, style="Green.TFrame")
        model_summary.grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 6))
        ttk.Label(model_summary, text="Scaling 1:", style="Green.TLabel").pack(side="left")
        ttk.Label(model_summary, textvariable=self.scaling1_method, style="Green.TLabel", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(3, 12))
        ttk.Label(model_summary, text="Scaling 2:", style="Green.TLabel").pack(side="left")
        ttk.Label(model_summary, textvariable=self.scaling2_method, style="Green.TLabel", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(3, 12))
        ttk.Label(model_summary, text="Scaling 3:", style="Green.TLabel").pack(side="left")
        ttk.Label(model_summary, textvariable=self.scaling3_method, style="Green.TLabel", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(3, 12))
        ttk.Label(model_summary, text="Scaling 4:", style="Green.TLabel").pack(side="left")
        ttk.Label(model_summary, textvariable=self.scaling4_method, style="Green.TLabel", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(3, 0))
        rows = [
            ("VSR Python", self.native_sr_python, False, [("Python executable", "python.exe"), ("EXE", "*.exe")]),
            ("Repository", self.native_sr_repo, True, None),
            ("Config", self.native_sr_config, False, [("Python config", "*.py")]),
            ("Checkpoint", self.native_sr_checkpoint, False, [("Checkpoint", "*.pth")]),
        ]
        for r, (name, variable, is_dir, filetypes) in enumerate(rows, start=2):
            ttk.Label(b, text=name, style="Green.TLabel").grid(row=r, column=0, sticky="w", pady=3, padx=(0, 4))
            ttk.Entry(b, textvariable=variable, width=27).grid(row=r, column=1, sticky="ew", pady=3)
            if is_dir:
                command = lambda v=variable: self._browse_dir_var(v)
            else:
                command = lambda v=variable, ft=filetypes: self._browse_file_var(v, (ft or []) + [("All files", "*")])
            ttk.Button(b, text="...", width=3, command=command).grid(row=r, column=2, padx=(3, 0), pady=3)
        opts = ttk.Frame(b, style="Green.TFrame")
        opts.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(8, 2))
        ttk.Label(opts, text="Chunk:", style="Green.TLabel").pack(side="left")
        ttk.Combobox(opts, textvariable=self.native_sr_chunk_frames,
                     values=["2", "3", "4", "6", "8", "12", "16", "24", "32", "48"], width=5, state="readonly").pack(side="left", padx=(4, 12))
        ttk.Label(opts, text="BasicVSR++: GPU model persistent; raw frames streamed in RAM",
                  style="Green.TLabel").pack(side="left", padx=(0, 12))
        ttk.Label(opts, text="Max seq:", style="Green.TLabel").pack(side="left")
        ttk.Combobox(opts, textvariable=self.native_sr_max_seq_len,
                     values=["None", "8", "12", "16", "24", "32"], width=6).pack(side="left", padx=(4, 0))
        tprof = ttk.Frame(b, style="Green.TFrame")
        tprof.grid(row=9, column=0, columnspan=3, sticky="w", pady=(5, 1))
        ttk.Label(tprof, text="BasicVSR++ tile profile:", style="Green.TLabel").pack(side="left")
        ttk.Combobox(tprof, textvariable=self.basicvsr_tile_profile,
                     values=["Balanced (512x288)", "Fast large tiles (768x432)",
                             "Conservative (384x216)"], width=29,
                     state="readonly").pack(side="left", padx=(5, 0))
        ttk.Label(b, text="The file inventory at left shows all resolved tool paths, "
                  "statuses and the VSR inference script. Select a row to view its full path; "
                  "double-click it to change its location.", style="Green.TLabel",
                  wraplength=400, justify="left").grid(row=7, column=0, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Label(b, text="V259 speed: BasicVSR++ streams RGB and BGR frames via RAM pipes. The GPU model stays loaded. Overlapping spatial neural tiles "
                  "for HD inputs (and smaller tiles on CUDA OOM) are blended in RAM; "
                  "no conventional enlargement is substituted. Tiling can affect edge consistency. "
                  "The 4X neural stage remains required even for a final 1X preseed target.",
                  style="Green.TLabel", wraplength=400,
                  justify="left").grid(row=8, column=0, columnspan=3, sticky="w", pady=(8, 0))

    def _native_sr_select_model_defaults(self, _event=None):
        """Choose matching known config/checkpoint paths; never overwrite the Python env."""
        if self.native_sr_model.get() == "BasicVSRPlusPlus_x4":
            base = Path(r"C:\Upscaler\BasicVSR_PP")
            self.native_sr_repo.set(str(base))
            self.native_sr_config.set(str(base / "configs" / "basicvsr_plusplus_reds4.py"))
            self.native_sr_checkpoint.set(str(base / "checkpoints" / "basicvsr_plusplus_reds4.pth"))
        else:
            base = Path(r"C:\Upscaler\RealBasicVSR")
            self.native_sr_repo.set(str(base))
            self.native_sr_config.set(str(base / "configs" / "realbasicvsr_x4.py"))
            self.native_sr_checkpoint.set(str(base / "checkpoints" / "RealBasicVSR_x4.pth"))

    def _build_seed_advanced_tab(self, p):
        b = ttk.LabelFrame(p, text="Legacy SeedVR2 INT8: effective workflow parameters", style="Green.TLabelframe", padding=10)
        b.pack(fill="x")
        for c in range(6):
            b.columnconfigure(c, weight=1 if c % 2 else 0)

        ttk.Label(b, text="Parameter mode:", style="Green.TLabel").grid(row=0, column=0, sticky="w")
        self.seed_parameter_mode_box = ttk.Combobox(
            b, textvariable=self.seed_parameter_mode,
            values=list(SEED_PARAMETER_MODES), width=30, state="readonly",
        )
        self.seed_parameter_mode_box.grid(row=0, column=1, columnspan=3, sticky="w", padx=(6, 18))
        ttk.Label(b, text="1080p Auto reference: 37 / 2 / 512 / 32", style="Green.TLabel").grid(
            row=0, column=4, columnspan=2, sticky="w")

        ttk.Label(b, text="Max temporal batch:", style="Green.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.seed_batch_box = ttk.Combobox(
            b, textvariable=self.seed_batch_max,
            values=["Auto"] + [str(n) for n in range(5, 50, 4)],
            width=11, state="normal",
        )
        self.seed_batch_box.grid(row=1, column=1, sticky="w", padx=(6, 18), pady=(8, 0))
        ttk.Label(b, text="Batch overlap (frames):", style="Green.TLabel").grid(row=1, column=2, sticky="w", pady=(8, 0))
        self.seed_overlap_box = ttk.Combobox(
            b, textvariable=self.seed_temporal_overlap,
            values=["Auto", "0", "2", "4", "8", "12"], width=9, state="normal",
        )
        self.seed_overlap_box.grid(row=1, column=3, sticky="w", padx=(6, 18), pady=(8, 0))
        ttk.Label(b, text="VAE tile (pixels):", style="Green.TLabel").grid(row=1, column=4, sticky="w", pady=(8, 0))
        self.seed_tile_box = ttk.Combobox(
            b, textvariable=self.seed_vae_tile,
            values=["256", "384", "512", "640", "768", "896", "1024"], width=10, state="normal",
        )
        self.seed_tile_box.grid(row=1, column=5, sticky="w", padx=6, pady=(8, 0))

        ttk.Label(b, text="VAE spatial overlap (px):", style="Green.TLabel").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.seed_vae_overlap_box = ttk.Combobox(
            b, textvariable=self.seed_vae_spatial_overlap,
            values=["Auto", "0", "32", "64", "128", "192", "256", "320", "384", "512"], width=11, state="normal",
        )
        self.seed_vae_overlap_box.grid(row=2, column=1, sticky="w", padx=(6, 18), pady=(8, 0))

        ttk.Label(
            b, text="Conventional conditioning: bicubic (fixed) -> ONE SeedVR2 diffusion pass. No Lanczos enlargement.",
            style="Green.TLabel", wraplength=850,
        ).grid(row=2, column=2, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Label(
            b,
            text=(""
                  ""
                  ""
                  ""),
            style="Green.TLabel", wraplength=1050,
        ).grid(row=3, column=0, columnspan=6, sticky="w", pady=(11, 0))

        ttk.Checkbutton(
            b, text="Disable DynamicVRAM (experimental; may cause OOM)",
            variable=self.comfy_disable_dynamic_vram, style="Green.TCheckbutton",
        ).grid(row=6, column=0, columnspan=3, sticky="w", pady=(9, 0))
        ttk.Checkbutton(
            b, text="Disable asynchronous weight offload (experimental)",
            variable=self.comfy_disable_async_offload, style="Green.TCheckbutton",
        ).grid(row=6, column=3, columnspan=3, sticky="w", pady=(9, 0))
        ttk.Label(
            b, text=(""
                     ""
                     ""),
            style="Green.TLabel", wraplength=1050,
        ).grid(row=7, column=0, columnspan=6, sticky="w", pady=(9, 0))
        ttk.Label(
            b, text=(""
                  ""
                  ""
                  ""),
            style="Green.TLabel", wraplength=1050,
        ).grid(row=5, column=0, columnspan=6, sticky="w", pady=(8, 0))

        preview = ttk.LabelFrame(p, text="Effective parameters for queued videos (before any OOM backoff)",
                                 style="Green.TLabelframe", padding=10)
        preview.pack(fill="both", expand=True, pady=(10, 0))
        ttk.Label(preview, textvariable=self.seed_effective_summary,
                  style="Green.TLabel", wraplength=1050).pack(fill="x", pady=(0, 6))
        columns = ("video", "resolution", "batch", "temporal", "tile", "spatial")
        self.seed_effective_table = ttk.Treeview(preview, columns=columns, show="headings", height=6)
        headers = {"video": "Queued video", "resolution": "AI output (estimated)",
                   "batch": "Frames / batch", "temporal": "Temporal overlap", "tile": "VAE tile (px)",
                   "spatial": "Spatial overlap (px)"}
        widths = {"video": 300, "resolution": 150, "batch": 120,
                  "temporal": 150, "tile": 110, "spatial": 160}
        for col in columns:
            self.seed_effective_table.heading(col, text=headers[col])
            self.seed_effective_table.column(col, width=widths[col], minwidth=90, anchor="w", stretch=col == "video")
        frame = ttk.Frame(preview)
        frame.pack(fill="both", expand=True)
        self.seed_effective_table.pack(in_=frame, side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.seed_effective_table.yview)
        scrollbar.pack(side="right", fill="y")
        self.seed_effective_table.configure(yscrollcommand=scrollbar.set)
        ttk.Label(preview, text="Preview uses estimated SeedVR2 output geometry. Actual settings, including "
                  "any VRAM backoff, are logged when each video starts. Different resolutions can have "
                  "different batches in the same queue.", style="Green.TLabel", wraplength=1050).pack(
            fill="x", pady=(6, 0))

    def _build_rife_tab(self, p):
        b = ttk.LabelFrame(
            p,
            text="RIFE frame interpolation - in-memory only",
            style="Purple.TLabelframe",
            padding=10,
        )
        b.pack(fill="x")

        ttk.Checkbutton(
            b,
            text="Enable RIFE frame interpolation",
            variable=self.rife_enable,
            style="Purple.TCheckbutton",
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(b, text="Mode:", style="Purple.TLabel").grid(
            row=0, column=2, sticky="e", padx=(20, 5)
        )
        ttk.Combobox(
            b,
            textvariable=self.rife_mode,
            values=RIFE_MODES,
            state="readonly",
            width=12,
        ).grid(row=0, column=3, sticky="w")

        ttk.Label(b, text="Increase:", style="Purple.TLabel").grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )
        self.rife_multiplier_box = ttk.Combobox(
            b,
            textvariable=self.rife_multiplier,
            values=["2X", "3X", "4X", "6X", "8X", "10X"],
            state="readonly",
            width=6,
        )
        self.rife_multiplier_box.grid(row=1, column=1, sticky="w", pady=(8, 0))

        ttk.Label(b, text="Target RIFE FPS:", style="Purple.TLabel").grid(
            row=1, column=2, sticky="e", padx=(20, 5), pady=(8, 0)
        )
        self.rife_target_spin = ttk.Spinbox(
            b,
            textvariable=self.rife_target_fps,
            from_=1,
            to=480,
            increment=1,
            width=8,
        )
        self.rife_target_spin.grid(row=1, column=3, sticky="w", pady=(8, 0))
        ttk.Label(b, text="FPS", style="Purple.TLabel").grid(
            row=1, column=4, sticky="w", padx=(4, 0), pady=(8, 0)
        )



    def _build_encode_tab(self, p):
        b = ttk.LabelFrame(p, text="Final H.265 / HEVC encode", style="Peach.TLabelframe", padding=10)
        b.pack(fill="x")
        for c in range(8):
            b.columnconfigure(c, weight=1 if c in (1, 3, 5, 7) else 0)

        ttk.Label(b, text="Encoder", style="Peach.TLabel").grid(row=0, column=0, sticky="w")
        self.encode_backend_box = ttk.Combobox(
            b,
            textvariable=self.encode_backend,
            values=ENCODE_BACKENDS,
            state="readonly",
            width=31,
        )
        self.encode_backend_box.grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(b, text="Quality", style="Peach.TLabel").grid(row=0, column=2, sticky="e")
        self.encode_quality_box = ttk.Combobox(
            b,
            textvariable=self.encode_quality,
            state="readonly",
            width=13,
        )
        self.encode_quality_box.grid(row=0, column=3, sticky="w", padx=6)

        ttk.Label(b, text="libx265 CPU cores", style="Peach.TLabel").grid(row=0, column=4, sticky="e")
        self.x265_threads_spin = ttk.Combobox(
            b,
            textvariable=self.x265_threads,
            values=tuple(range(1, max(1, int(os.cpu_count() or 1)) + 1)),
            state="readonly",
            width=7,
        )
        self.x265_threads_spin.grid(row=0, column=5, sticky="w", padx=6)

        ttk.Label(b, text="HEVC 10-bit", style="Peach.TLabel", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=6, sticky="e", padx=(12, 4)
        )
        ttk.Label(b, text="MP4 only", style="Peach.TLabel", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=7, sticky="w", padx=6
        )

        ttk.Label(
            b,
            textvariable=self.auto_bitrate_preview,
            style="Peach.TLabel",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=1, column=0, columnspan=8, sticky="w", pady=(10, 0))

        self._update_encode_controls()


    def _build_tools_tab(self, p):
        b = ttk.LabelFrame(p, text="Hidden ComfyUI backend", style="Blue.TLabelframe", padding=9)
        b.pack(fill="x", pady=(0, 7))
        b.columnconfigure(1, weight=1)
        ttk.Label(b, text="ComfyUI portable root", style="Blue.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(b, textvariable=self.comfy_root).grid(row=0, column=1, sticky="ew", padx=7)
        ttk.Button(b, text="Browse...", command=lambda: self._browse_dir_var(self.comfy_root)).grid(row=0, column=2)

        ttk.Label(b, text="NVIDIA launch mode", style="Blue.TLabel").grid(row=1, column=0, sticky="nw", pady=(7, 0))
        fast_mode_check = ttk.Checkbutton(
            b,
            text="Use NVIDIA Fast mode (FP16 accumulation)",
            variable=self.comfy_launch_mode,
            onvalue="NVIDIA Fast",
            offvalue="Standard NVIDIA",
            command=self._update_comfy_command_preview
        )
        fast_mode_check.grid(row=1, column=1, columnspan=2, sticky="w", padx=7, pady=(7, 0))

        ttk.Label(b, text="Hidden ComfyUI command", style="Blue.TLabel").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(
            b,
            textvariable=self.comfy_command_preview,
            state="readonly",
        ).grid(row=2, column=1, columnspan=2, sticky="ew", padx=7, pady=(6, 0))

        ttk.Label(b, text="SeedVR2 API workflow JSON", style="Blue.TLabel").grid(row=3, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(b, textvariable=self.workflow_json).grid(row=3, column=1, sticky="ew", padx=7, pady=(6, 0))
        ttk.Button(b, text="Browse...", command=lambda: self._browse_file_var(self.workflow_json, [("JSON", "*.json"), ("All", "*")])).grid(row=3, column=2, pady=(6, 0))
        ttk.Label(b, text="Hidden port", style="Blue.TLabel").grid(row=4, column=0, sticky="w", pady=(6, 0))
        ttk.Spinbox(b, textvariable=self.comfy_port, from_=1024, to=65535, width=8).grid(row=4, column=1, sticky="w", padx=7, pady=(6, 0))
        ttk.Button(b, text="Validate workflow", command=self._validate_workflow_button).grid(row=4, column=2, pady=(6, 0))
        self._update_comfy_command_preview()



    def _build_files_tab(self, p):
        top = ttk.LabelFrame(p, text="Required files and installation status", style="Blue.TLabelframe", padding=6)
        top.pack(fill="both", expand=True)


        rootrow = ttk.Frame(top, style="Blue.TFrame")
        rootrow.pack(fill="x", pady=(0, 5))
        ttk.Label(rootrow, text="Tool root:", style="Blue.TLabel", font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Entry(rootrow, textvariable=self.install_root, width=28).pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(rootrow, text="...", width=3, command=self._browse_install_root).pack(side="left")
        actions = ttk.Frame(top, style="Blue.TFrame")
        actions.pack(fill="x", pady=(0, 3))
        ttk.Button(actions, text="Scan root", command=self._scan_install_root_button).pack(side="left")
        ttk.Button(actions, text="Refresh", command=self._refresh_files_status).pack(side="left", padx=3)
        ttk.Button(actions, text="Browse / Fix", command=self._fix_selected_file_item).pack(side="left", padx=3)
        ttk.Button(actions, text="Test", command=self._test_installation_button).pack(side="left", padx=3)

        self.files_test_status = tk.StringVar(value="Installation test: not run")
        ttk.Label(top, textvariable=self.files_test_status, style="Blue.TLabel", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

        cols = ("component", "status", "location")
        table_wrap = ttk.Frame(top, style="Blue.TFrame")
        table_wrap.pack(fill="both", expand=True)
        table_wrap.rowconfigure(0, weight=1)
        table_wrap.columnconfigure(0, weight=1)

        self.files_tree = ttk.Treeview(table_wrap, columns=cols, show="headings", height=17, style="Files.Treeview")
        self._files_sort_reverse = {c: False for c in cols}
        self._files_full_details = {}
        for col, label in (("component", "Component"), ("status", "Status"), ("location", "Location / details")):
            self.files_tree.heading(col, text=label, command=lambda c=col: self._sort_files_column(c))
        self.files_tree.column("component", width=172, minwidth=125, anchor="w", stretch=False)
        self.files_tree.column("status", width=65, minwidth=55, anchor="center", stretch=False)
        self.files_tree.column("location", width=490, minwidth=240, anchor="w", stretch=True)
        self.files_tree.tag_configure("ok", background=PASTEL["green"])
        self.files_tree.tag_configure("warn", background=PASTEL["yellow"])
        self.files_tree.tag_configure("bad", background=PASTEL["red"])

        files_vscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.files_tree.yview)
        files_hscroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.files_tree.xview)
        self.files_tree.configure(yscrollcommand=files_vscroll.set, xscrollcommand=files_hscroll.set)
        self.files_tree.grid(row=0, column=0, sticky="nsew")
        files_vscroll.grid(row=0, column=1, sticky="ns")
        files_hscroll.grid(row=1, column=0, sticky="ew")

        detail_box = ttk.LabelFrame(top, text="Selected row details", style="Blue.TLabelframe", padding=3)
        detail_box.pack(fill="x", pady=(4, 0))
        self.files_detail_text = tk.Text(detail_box, height=2, wrap="word", bg="#FFFFFF", fg=PASTEL["text"], relief="solid", borderwidth=1)
        self.files_detail_text.pack(fill="x")
        self.files_detail_text.insert("1.0", "")
        self.files_detail_text.configure(state="disabled")

        self.files_tree.bind("<Double-1>", lambda _e: self._fix_selected_file_item())
        self.files_tree.bind("<<TreeviewSelect>>", self._show_selected_file_detail)


    def _browse_install_root(self):
        p = filedialog.askdirectory(title="Select the single root folder containing the upscaling tools")
        if p:
            self.install_root.set(p)
            self._scan_install_root_button()

    @staticmethod
    def _path_score(path: Path, preferred_words: Tuple[str, ...]) -> Tuple[int, int, str]:
        low = str(path).lower()
        score = sum(1 for w in preferred_words if w in low)
        return (-score, len(path.parts), low)

    def _discover_api_workflow_under(self, root: Path) -> Optional[Path]:
        candidates: List[Path] = []
        try:
            for p in root.rglob("*.json"):
                low = p.name.lower()
                if "seed" in low or "workflow" in low or "api" in low:
                    candidates.append(p)
        except Exception:
            return None
        candidates.sort(key=lambda p: self._path_score(p, ("seedvr2", "api", "workflow")))
        for p in candidates[:80]:
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    continue
                nodes = [v for v in data.values() if isinstance(v, dict) and "class_type" in v]
                if nodes and any("seedvr2" in str(v.get("class_type", "")).lower() for v in nodes):
                    return p
            except Exception:
                continue
        return None

    def _scan_install_root_button(self):
        root = Path(self.install_root.get().strip())
        if not root.is_dir():
            messagebox.showwarning(APP_NAME, "Choose an existing upscaling root folder first.")
            return
        if hasattr(self, "files_test_status"):
            self.files_test_status.set(f"Scanning root: {root} ...")
        threading.Thread(target=self._scan_install_root_worker, args=(root,), daemon=True).start()

    def _scan_install_root_worker(self, root: Path):
        try:
            hits: Dict[str, List[Path]] = {
                "ffmpeg": [], "ffprobe": [], "vspipe": [], "main": [], "python_embeded": [],
                "rife": [], "rife_models": [], "rife_archives": [], "source": []
            }
            skip_dirs = {"video upscaled", "moviesupscalled", "temp", "__pycache__", ".git", "node_modules"}
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d.lower() not in skip_dirs]
                d = Path(dirpath)
                lows = {name.lower(): name for name in filenames}
                if "ffmpeg.exe" in lows:
                    hits["ffmpeg"].append(d / lows["ffmpeg.exe"])
                if "ffprobe.exe" in lows:
                    hits["ffprobe"].append(d / lows["ffprobe.exe"])
                if "vspipe.exe" in lows:
                    hits["vspipe"].append(d / lows["vspipe.exe"])
                if "vspipe.bat" in lows:
                    hits["vspipe"].append(d / lows["vspipe.bat"])
                if d.name.lower() == "comfyui" and "main.py" in lows:
                    hits["main"].append(d / lows["main.py"])
                if d.name.lower() == "python_embeded" and "python.exe" in lows:
                    hits["python_embeded"].append(d / lows["python.exe"])
                path_has_rife = any("rife" in part.lower() for part in d.parts)
                models_here = d / "models"
                has_rife_models = False
                if models_here.is_dir():
                    try:
                        has_rife_models = any(x.is_dir() and "rife" in x.name.lower() for x in models_here.iterdir())
                    except Exception:
                        pass

                if "flownet.param" in lows and "flownet.bin" in lows and "rife" in str(d).lower():
                    hits["rife_models"].append(d)
                for name in filenames:
                    low = name.lower()
                    p = d / name
                    if low.endswith(".dll"):
                        if "rife" in low or path_has_rife or has_rife_models:
                            hits["rife"].append(p)
                        if "ffms2" in low or "lsmash" in low or "bestsource" in low:
                            hits["source"].append(p)
                    elif low.endswith((".zip", ".7z")) and "rife" in low:
                        hits["rife_archives"].append(p)

            def pick(key: str, words: Tuple[str, ...] = ()) -> Optional[Path]:
                xs = hits.get(key, [])
                return sorted(xs, key=lambda p: self._path_score(p, words))[0] if xs else None

            ffmpeg = pick("ffmpeg", ("ffmpeg", "bin", "comfyui"))
            ffprobe = pick("ffprobe", ("ffmpeg", "bin", "comfyui"))
            vspipe = pick("vspipe", ("vapoursynth", "site-packages"))

            comfy_root = None
            for main in sorted(hits["main"], key=lambda p: self._path_score(p, ("comfyui_windows_portable", "comfyui"))):
                candidate = main.parent.parent
                if (candidate / "python_embeded" / "python.exe").is_file():
                    comfy_root = candidate
                    break
            if comfy_root is None and hits["main"]:
                comfy_root = hits["main"][0].parent.parent

            workflow = self._discover_api_workflow_under(root)
            rife_candidates = hits.get("rife", [])
            rife_dll = None
            if rife_candidates:
                rife_candidates = sorted(
                    rife_candidates,
                    key=lambda p: (
                        0 if p.name.lower() == "librife_windows_x86-64.dll" else 1,
                        0 if "rife" in p.name.lower() else 1,
                        self._path_score(p, ("tools", "vapoursynth", "plugins", "rife")),
                    )
                )
                rife_dll = rife_candidates[0]

            rife_model = None
            if hits.get("rife_models"):
                models = sorted(
                    hits["rife_models"],
                    key=lambda p: (
                        0 if p.name.lower() == "rife-v4.6" else 1,
                        0 if "rife-v4" in p.name.lower() else 1,
                        len(str(p)),
                    )
                )
                rife_model = models[0]

            source_dll = pick("source", ("vapoursynth", "plugins", "bestsource", "ffms2", "lsmash"))
            result = {
                "root": str(root),
                "ffmpeg": str(ffmpeg) if ffmpeg else "",
                "ffprobe": str(ffprobe) if ffprobe else "",
                "vspipe": str(vspipe) if vspipe else "",
                "comfy_root": str(comfy_root) if comfy_root else "",
                "workflow": str(workflow) if workflow else "",
                "rife_hint": str(rife_dll or ""),
                "rife_plugin_dll": str(rife_dll or ""),
                "rife_plugin_dir": str(rife_dll.parent) if rife_dll else "",
                "rife_model_path": str(rife_model or ""),
                "rife_archive_hint": str(pick("rife_archives", ("rife",)) or ""),
                "source_hint": str(source_dll or ""),
                "vs_source_plugin_dll": str(source_dll or ""),
            }
            self._post("root_scan_result", result)
        except Exception as e:
            self._post("files_test_status", (f"Root scan failed: {e}", False))

    def _apply_root_scan_result(self, result: Dict[str, str]):
        if result.get("ffmpeg"):
            self.ffmpeg.set(result["ffmpeg"])
        if result.get("ffprobe"):
            self.ffprobe.set(result["ffprobe"])
        if result.get("vspipe"):
            self.vspipe.set(result["vspipe"])
        if result.get("comfy_root"):
            self.comfy_root.set(result["comfy_root"])
        if result.get("workflow"):
            self.workflow_json.set(result["workflow"])
        if result.get("rife_plugin_dir"):
            self.rife_plugin_dir.set(result["rife_plugin_dir"])
        if result.get("rife_plugin_dll"):
            self.rife_plugin_dll.set(result["rife_plugin_dll"])
        if result.get("rife_model_path"):
            self.rife_model_path.set(result["rife_model_path"])
        if result.get("vs_source_plugin_dll"):
            self.vs_source_plugin_dll.set(result["vs_source_plugin_dll"])
        found = [k for k in ("ffmpeg", "ffprobe", "vspipe", "comfy_root", "workflow", "rife_plugin_dll", "rife_model_path", "vs_source_plugin_dll") if result.get(k)]
        self._log(f"Root scan completed under {result.get('root')}. Auto-filled: {', '.join(found) if found else 'none'}")
        if result.get("rife_hint"):
            self._log(f"RIFE plugin DLL found: {result['rife_hint']}")
        if result.get("rife_model_path"):
            self._log(f"RIFE model folder found: {result['rife_model_path']}")
        elif result.get("rife_archive_hint"):
            self._log(f"RIFE archive found but not extracted: {result['rife_archive_hint']}")
        if result.get("source_hint"):
            self._log(f"VapourSynth source plugin candidate found: {result['source_hint']}")
        self.files_test_status.set("Root scan finished; verifying discovered components...")
        self.after(150, self._refresh_files_status)


    @staticmethod
    def _safe_move_folder_name(value: str, fallback: str) -> str:
        name = str(value or "").strip()
        if not name:
            return fallback
        for bad in ('\\', '/', ':', '*', '?', '"', '<', '>', '|'):
            name = name.replace(bad, "_")
        name = name.strip(" .")
        return name or fallback

    def _update_move_processed_controls(self) -> None:
        enabled = bool(self.move_processed_enable.get())
        state = "normal" if enabled else "disabled"
        if hasattr(self, "move_success_entry"):
            self.move_success_entry.configure(state=state)
        if hasattr(self, "move_failed_entry"):
            self.move_failed_entry.configure(state=state)
        if hasattr(self, "move_success_browse"):
            self.move_success_browse.configure(state=state)
        if hasattr(self, "move_failed_browse"):
            self.move_failed_browse.configure(state=state)

    def _queue_first_original_parent(self) -> Optional[Path]:
        if self.jobs:
            ordered = sorted(
                self.jobs,
                key=lambda j: (
                    int(j.process_order) if int(j.process_order or 0) > 0 else 10**9,
                    self.jobs.index(j),
                ),
            )
            first = ordered[0]
            original = Path(first.original_path) if first.original_path else Path(first.info.path)
            return original.parent

        raw = str(self.input_path.get() or "").strip()
        if raw:
            first = raw.split(" | ", 1)[0].strip()
            if first:
                p = Path(first)
                return p.parent if p.is_file() else p
        return None

    @staticmethod
    def _v263_resolve_output_root(base: Path) -> Path:
        """Reuse an existing VideoUpscaled ancestor instead of nesting it repeatedly."""
        base = Path(base)
        for candidate in (base, *base.parents):
            if candidate.name.casefold() == DEFAULT_OUTPUT_FOLDER.casefold():
                return candidate
        return base / DEFAULT_OUTPUT_FOLDER

    @staticmethod
    def _v263_safe_component(
        folder: Path,
        prefix: str,
        suffix: str,
        identity: str = "",
        max_full_length: int = 238,
        max_component_length: int = 210,
    ) -> str:
        """Preserve normal names; shorten long Windows paths without losing the final tag.

        A ten-digit SHA256 identity distinguishes similarly named long source files.
        The resulting Windows path is kept below legacy FFmpeg/Windows MAX_PATH.
        """
        full_name = prefix + suffix
        if (len(full_name) <= max_component_length
                and len(str(Path(folder) / full_name)) <= max_full_length):
            return full_name
        budget = min(max_component_length, max_full_length - len(str(folder)) - 1)
        if budget < 31:
            raise BackendError(
                f"Output folder path is too long for reliable Windows/FFmpeg encoding: {folder}. "
                "Move the source to a shorter folder or choose a shorter destination."
            )
        signature = hashlib.sha256((identity or full_name).encode('utf-8', 'surrogatepass')).hexdigest()[:10]
        digest = '_' + signature
        # Keep key processing information at the end of the filename. A very long
        # suffix is separately compressed, but the extension is always preserved.
        if len(suffix) + len(digest) + 12 > budget:
            stem = Path(suffix).stem
            ext = Path(suffix).suffix
            preserved = stem[-max(8, budget - len(digest) - len(ext) - 14):]
            suffix = '_' + preserved.lstrip('_') + ext
        head_size = budget - len(suffix) - len(digest)
        if head_size < 1:
            raise BackendError(f"Filename cannot fit under the Windows path limit: {folder}")
        clipped = prefix[:head_size].rstrip(' ._')
        if not clipped:
            clipped = 'video'[:head_size]
        result = clipped + digest + suffix
        if len(str(Path(folder) / result)) > max_full_length or len(result) > max_component_length:
            raise BackendError(f"Failed to safely shorten output filename: {folder / result}")
        return result

    def _dynamic_output_root(self) -> Optional[Path]:
        base = self._queue_first_original_parent()
        return self._v263_resolve_output_root(base) if base is not None else None

    def _update_dynamic_path_preview(self) -> None:
        if not hasattr(self, "dynamic_paths_text"):
            return
        base = self._queue_first_original_parent()
        if base is None:
            self.dynamic_paths_text.set(
                f"Dynamic folders: <first movie folder>\\{DEFAULT_SUCCESS_FOLDER} | "
                f"<first movie folder>\\{DEFAULT_FAILED_FOLDER} | "
                f"<first movie folder>\\{DEFAULT_OUTPUT_FOLDER}"
            )
            return
        self.dynamic_paths_text.set(
            f"Dynamic folders from first movie: "
            f"{base / DEFAULT_SUCCESS_FOLDER} | "
            f"{base / DEFAULT_FAILED_FOLDER} | "
            f"{self._v263_resolve_output_root(base)}"
        )

    def _processed_move_folder_values(self) -> Tuple[str, str]:
        success = str(
            self._run_move_success_folder
            if self._run_move_success_folder is not None
            else self.move_success_folder.get()
        ).strip() or DEFAULT_SUCCESS_FOLDER
        failed = str(
            self._run_move_failed_folder
            if self._run_move_failed_folder is not None
            else self.move_failed_folder.get()
        ).strip() or DEFAULT_FAILED_FOLDER
        return success, failed

    def _move_destination_directory(self, source: Path, configured: str, fallback: str) -> Path:
        value = str(configured or "").strip()
        if not value:
            value = fallback
        p = Path(value).expanduser()
        if p.is_absolute():
            return p
        base = self._queue_first_original_parent()
        if base is None:
            base = Path(source).parent
        return base / self._safe_move_folder_name(value, fallback)

    @staticmethod
    def _move_folder_leaf_name(configured: str, fallback: str) -> str:
        value = str(configured or "").strip()
        if not value:
            return fallback
        try:
            name = Path(value).name
        except Exception:
            name = value
        return name or fallback

    @staticmethod
    def _unique_move_destination(destination: Path) -> Path:
        if not destination.exists():
            return destination
        stem = destination.stem
        suffix = destination.suffix
        for n in range(1, 100000):
            candidate = destination.with_name(f"{stem}_{n}{suffix}")
            if not candidate.exists():
                return candidate
        raise BackendError(f"Could not create a unique destination name for {destination.name}")

    def _move_source_after_processing(self, job: Job, success: bool) -> Optional[Path]:
        enabled = (
            bool(self._run_move_processed_enable)
            if self._run_move_processed_enable is not None
            else bool(self.move_processed_enable.get())
        )
        if not enabled:
            return None

        source = Path(job.info.path)
        if not source.is_file():
            self._post("log", f"SOURCE MOVE WARNING: source file no longer exists: {source}")
            return None

        success_folder, failed_folder = self._processed_move_folder_values()
        configured = success_folder if success else failed_folder
        fallback = DEFAULT_SUCCESS_FOLDER if success else DEFAULT_FAILED_FOLDER
        destination_dir = self._move_destination_directory(source, configured, fallback)
        destination_dir.mkdir(parents=True, exist_ok=True)

        try:
            if source.parent.resolve() == destination_dir.resolve():
                return source
        except Exception:
            pass

        destination = self._unique_move_destination(destination_dir / source.name)
        try:
            moved = Path(shutil.move(str(source), str(destination)))
        except Exception as e:
            self._post(
                "log",
                f"SOURCE MOVE WARNING: processing {'succeeded' if success else 'failed'}, "
                f"but the source could not be moved: {source} -> {destination}: {e}",
            )
            return None

        job.info.path = moved
        if job.ai_info is not None and Path(job.ai_info.path) == source:
            job.ai_info.path = moved
        self._post(
            "log",
            f"SOURCE MOVED AFTER {'SUCCESS' if success else 'FAILURE'}: {source} -> {moved}",
        )
        return moved

    def _browse_input(self):
        if self.input_mode.get() == "folder":
            p = filedialog.askdirectory(title="Choose video folder")
            if p:
                self.input_path.set(p)
                self.after(30, self._scan_input)
        else:
            paths = filedialog.askopenfilenames(
                title="Choose one or more videos",
                filetypes=[
                    ("Video files", "*.mp4 *.mkv *.mov *.avi *.m4v *.mpeg *.mpg *.mts *.m2ts *.ts *.webm *.wmv *.flv *.vob"),
                    ("All files", "*"),
                ],
            )
            if paths:
                self.input_path.set(" | ".join(str(p) for p in paths))
                self.after(30, self._scan_input)

    def _browse_move_success_folder(self):
        p = filedialog.askdirectory(title="Choose folder for successfully processed source movies")
        if p:
            self.move_success_folder.set(p)

    def _browse_move_failed_folder(self):
        p = filedialog.askdirectory(title="Choose folder for failed source movies")
        if p:
            self.move_failed_folder.set(p)

    def _browse_output_parent(self):
        p = filedialog.askdirectory(title="Choose output parent folder")
        if p:
            self.output_parent.set(p)

    def _browse_file_var(self, var: tk.StringVar, types):
        p = filedialog.askopenfilename(filetypes=types)
        if p:
            var.set(p)

    def _browse_dir_var(self, var: tk.StringVar):
        p = filedialog.askdirectory()
        if p:
            var.set(p)

    def _scan_input(self):
        raw = self.input_path.get().strip()
        if not raw:
            messagebox.showwarning(APP_NAME, "Choose a video or folder first.")
            return
        if self.input_mode.get() == "file":
            files = []
            for part in raw.split(" | "):
                cleaned = part.strip().strip('"').strip("'")
                if not cleaned:
                    continue
                candidate = Path(cleaned)
                if candidate.is_file():
                    files.append(candidate)
                else:
                    self._post("log", f"INPUT WARNING: video file not found: {candidate}")
        else:
            p = Path(raw)
            files = []
            if p.is_dir():
                success_folder = self._move_folder_leaf_name(
                    self.move_success_folder.get(), DEFAULT_SUCCESS_FOLDER
                ).casefold()
                failed_folder = self._move_folder_leaf_name(
                    self.move_failed_folder.get(), DEFAULT_FAILED_FOLDER
                ).casefold()
                excluded_dirs = {
                    "video upscaled", "videoupscaled", "moviesupscalled",
                    "upscal done", "upscal failled", "originaldone",
                    "originalfailled", DEFAULT_SUCCESS_FOLDER.casefold(),
                    DEFAULT_FAILED_FOLDER.casefold(), DEFAULT_OUTPUT_FOLDER.casefold(),
                    success_folder, failed_folder,
                }

                try:
                    root_resolved = p.resolve()
                except Exception:
                    root_resolved = p

                def is_inside_excluded_subfolder(candidate: Path) -> bool:
                    try:
                        rel = candidate.resolve().relative_to(root_resolved)
                    except Exception:
                        try:
                            rel = candidate.relative_to(p)
                        except Exception:
                            return False
                    parent_parts = rel.parts[:-1]
                    return any(part.casefold() in excluded_dirs for part in parent_parts)

                try:
                    if self.recursive.get():
                        candidates = p.rglob("*")
                    else:
                        candidates = p.iterdir()
                    for x in candidates:
                        try:
                            if not x.is_file():
                                continue
                            if x.suffix.lower() not in VIDEO_EXTENSIONS:
                                continue
                            if is_inside_excluded_subfolder(x):
                                continue
                            files.append(x)
                        except (OSError, PermissionError):
                            continue
                except (OSError, PermissionError) as e:
                    self._post("log", f"Folder scan warning for {p}: {e}")

                self._post(
                    "log",
                    f"V151 FOLDER SCAN: root={p}; recursive={'ON' if self.recursive.get() else 'OFF'}; "
                    f"supported videos found={len(files)}.",
                )
        files = [x for x in files if x.suffix.lower() in VIDEO_EXTENSIONS]
        if not files:
            messagebox.showwarning(APP_NAME, "No supported video files were found.")
            return

        existing = {str(j.info.path.resolve()).lower() for j in self.jobs}
        added = 0
        ordered_files = files if self.input_mode.get() == "file" else sorted(files, key=lambda x: x.name.lower())
        for f in ordered_files:
            key = str(f.resolve()).lower()
            if key in existing:
                continue
            try:
                info = self._probe_video(f)
            except Exception as e:
                info = VideoInfo(path=f)
                self._post("log", f"Probe warning for {f.name}: {e}")
            job = Job(
                info=info,
                original_path=Path(f),
                process_order=self._next_processing_order(),
            )
            self._initialize_job_section2_settings(job)
            self.jobs.append(job)
            self._insert_job(job)
            existing.add(key)
            added += 1
        self._normalize_processing_order()
        self._update_dynamic_path_preview()
        self._refresh_preview()
        self._sort_queue_table("order", reverse=False)
        unknown = [j for j in self.jobs if j.info.width <= 0 or j.info.height <= 0]
        if unknown:
            self._post("log", f"Retrying metadata probe for {len(unknown)} unread video(s) with fallback detection.")
            for job in unknown:
                try:
                    job.info = self._probe_video(job.info.path)
                    self._update_job_row(job)
                except Exception as e:
                    self._post("log", f"Metadata read failed for {job.info.path.name}: {e}")
        self._update_total_queue_estimate()
        self._post("log", f"V265 VIDEO IMPORT: {added} new video(s); {len(self.tree.get_children(''))} visible queue rows; {len(self.jobs)} total job(s).")

    def _insert_job(self, job: Job):
        i = job.info
        # Insert the row before metadata-based ETA work. Large video fingerprinting
        # or an unreadable history record must never hide an imported video.
        try:
            out_w, out_h, out_fps, _factor = self._job_settings_call(job, self._output_geometry, i)
            ai_fps = self._job_settings_call(job, self._fps_reduction_plan, i)[0]
        except Exception as exc:
            out_w, out_h, out_fps, ai_fps = i.width, i.height, i.fps, i.fps
            self._post("log", f"Queue preview unavailable for {i.path.name}: {exc}")
        engine = "SeedVR2"
        job.tree_id = self.tree.insert("", "end", values=(
            str(job.process_order),
            i.path.name,
            self._engine_display_name(engine),
            self._planned_upscale_factor_text(i, job),
            f"{i.width}×{i.height}" if i.width else "?",
            f"{out_w}×{out_h}" if out_w and out_h else "?",
            self._fmt_fps(i.fps),
            self._fmt_fps(ai_fps),
            self._fmt_fps(out_fps),
            self._predicted_bitrate_text(i, job),
            self._fmt_time(i.duration),
            job.estimate_similarity_text,
            job.prediction_evidence,
            job.estimate_text,
            job.elapsed_text,
            job.eta,
            self._queue_progress_text(job),
        ))
        self._update_total_queue_estimate()
        self.after_idle(self._refresh_factor_overlays)
        # Keep initial queue display responsive; estimates update after rows appear.
        self.after(250, lambda j=job: self._update_new_job_eta(j))

    def _update_new_job_eta(self, job: Job) -> None:
        if job not in self.jobs or not job.tree_id:
            return
        try:
            self._update_job_duration_estimate(job)
            self._update_job_row(job)
            self._update_total_queue_estimate()
        except Exception as exc:
            job.estimate_text = "Learning..."
            job.prediction_evidence = "Estimate unavailable"
            self._post("log", f"ETA unavailable for {job.info.path.name}: {exc}")
            self._update_job_row(job)

    @staticmethod
    def _nearest_allowed_factor(value: float) -> float:
        choices = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 6.0, 6.5, 8.0, 8.5, 10.0, 12.0]
        value = max(1.5, min(12.0, float(value)))
        return min(choices, key=lambda x: (abs(x - value), x))

    @staticmethod
    def _factor_text(value: float) -> str:
        if abs(value - round(value)) < 1e-6:
            return f"{int(round(value))}X"
        return f"{value:g}X"

    def _predicted_bitrate_mbps(self, info: VideoInfo, job: Optional[Job] = None) -> float:
        def build() -> float:
            width, height, fps, _factor = self._output_geometry(info)
            return self._quality_bitrate(width, height, fps)
        try:
            return float(self._job_settings_call(job, build)) if isinstance(job, Job) else float(build())
        except Exception:
            return 0.0

    def _predicted_bitrate_text(self, info: VideoInfo, job: Optional[Job] = None) -> str:
        value = self._predicted_bitrate_mbps(info, job)
        return f"{value:.2f} Mb/s" if value > 0 else "?"

    @staticmethod
    def _queue_progress_text(job: Job) -> str:
        status = str(job.status or "--")
        stage = str(job.stage or "--")
        pct = max(0.0, min(100.0, float(job.progress or 0.0)))
        return f"{status} | {stage} | {pct:.0f}%"

    @staticmethod
    def _format_factor_for_queue(value: float) -> str:
        factor = float(value)
        rounded = round(factor)
        if abs(factor - rounded) < 0.005:
            return f"{int(rounded)}X"
        return f"{factor:.2f}X"

    def _planned_upscale_factor_text(self, info: VideoInfo, job: Optional[Job] = None) -> str:
        try:
            result = self._job_settings_call(job, self._output_geometry, info) if isinstance(job, Job) else self._output_geometry(info)
            return self._format_factor_for_queue(result[3])
        except Exception:
            return "?"


    def _factor_column_id(self) -> str:
        try:
            return f"#{self.queue_columns.index('factor') + 1}"
        except Exception:
            return "#4"

    def _hide_factor_overlay(self, job: Job) -> None:
        label = self._factor_overlays.get(job.tree_id)
        if label is not None:
            try:
                label.place_forget()
            except Exception:
                pass

    def _factor_overlay_click(self, event, tree_id: str):
        if not hasattr(self, "tree") or not self.tree.exists(tree_id):
            return "break"

        state = int(getattr(event, "state", 0) or 0)
        ctrl = bool(state & 0x0004)
        shift = bool(state & 0x0001)

        children = list(self.tree.get_children(""))
        current = list(self.tree.selection())

        if shift:
            anchor_id = self.tree.focus()
            if not anchor_id or anchor_id not in children:
                anchor_id = current[-1] if current else tree_id
            try:
                a = children.index(anchor_id)
                b = children.index(tree_id)
                lo, hi = sorted((a, b))
                range_ids = children[lo:hi + 1]
                if ctrl:
                    merged = list(dict.fromkeys(current + range_ids))
                    self.tree.selection_set(merged)
                else:
                    self.tree.selection_set(range_ids)
            except Exception:
                self.tree.selection_set(tree_id)
        elif ctrl:
            if tree_id in current:
                self.tree.selection_remove(tree_id)
            else:
                self.tree.selection_add(tree_id)
            self.tree.focus(tree_id)
        else:
            self.tree.selection_set(tree_id)
            self.tree.focus(tree_id)

        self.after_idle(self._refresh_factor_overlays)
        return "break"

    def _refresh_factor_overlays(self) -> None:
        if not hasattr(self, "_factor_overlays") or not hasattr(self, "tree"):
            return
        if not self.tree.winfo_exists():
            return

        active_ids = {job.tree_id for job in self.jobs if job.tree_id}
        for tree_id in list(self._factor_overlays):
            if tree_id not in active_ids:
                try:
                    self._factor_overlays[tree_id].destroy()
                except Exception:
                    pass
                self._factor_overlays.pop(tree_id, None)

        factor_col = self._factor_column_id()
        selected_ids = set(self.tree.selection())

        for job in self.jobs:
            if not job.tree_id or not self.tree.exists(job.tree_id):
                continue

            def overlay_state():
                engine = self._selected_engine()
                choice = self._selected_upscale_choice(engine)
                factor_text = self._planned_upscale_factor_text(job.info, job)
                return False, factor_text

            emphasize, factor_text = self._job_settings_call(job, overlay_state)
            label = self._factor_overlays.get(job.tree_id)

            if not emphasize:
                if label is not None:
                    try:
                        label.place_forget()
                    except Exception:
                        pass
                continue

            bbox = self.tree.bbox(job.tree_id, factor_col)
            if not bbox:
                if label is not None:
                    try:
                        label.place_forget()
                    except Exception:
                        pass
                continue

            x, y, width, height = bbox
            if label is None:
                label = tk.Label(
                    self.tree,
                    bd=0,
                    relief="flat",
                    fg="#7A0000",
                    font=("Segoe UI", 9, "bold"),
                    justify="center",
                    cursor="arrow",
                )
                self._factor_overlays[job.tree_id] = label
                label.bind(
                    "<Button-1>",
                    lambda e, jid=job.tree_id: self._factor_overlay_click(e, jid),
                )

            label.configure(
                text=factor_text,
                bg="#CFE3F6" if job.tree_id in selected_ids else "#FFFFFF",
                fg="#7A0000",
            )
            label.place(
                x=x + 1,
                y=y + 1,
                width=max(1, width - 2),
                height=max(1, height - 2),
            )

    def _update_job_row(self, job: Job):
        if not job.tree_id:
            return
        i = job.info
        try:
            out_w, out_h, out_fps, _factor = self._job_settings_call(job, self._output_geometry, i)
            ai_fps = self._job_settings_call(job, self._fps_reduction_plan, i)[0]
            engine = self._job_settings_call(job, self._selected_engine)
            if (job.verified_ai_output_width > 0 and job.verified_ai_output_height > 0
                    and job.status in ("Running", "Done")):
                out_w, out_h = job.verified_ai_output_width, job.verified_ai_output_height
            self.tree.item(job.tree_id, values=(
                str(job.process_order),
                i.path.name,
                self._engine_display_name(engine),
                self._planned_upscale_factor_text(i, job),
                f"{i.width}×{i.height}" if i.width else "?",
                f"{out_w}×{out_h}" if out_w and out_h else "?",
                self._fmt_fps(i.fps),
                self._fmt_fps(ai_fps),
                self._fmt_fps(out_fps),
                self._predicted_bitrate_text(i, job),
                self._fmt_time(i.duration),
                job.estimate_similarity_text,
                job.prediction_evidence,
                job.estimate_text,
                job.elapsed_text,
                job.eta,
                self._queue_progress_text(job),
            ))
            self.after_idle(self._refresh_factor_overlays)
        except tk.TclError:
            pass

    def _next_processing_order(self) -> int:
        if not self.jobs:
            return 1
        return max(0, max(int(j.process_order or 0) for j in self.jobs)) + 1

    def _normalize_processing_order(self) -> None:


        ordered = sorted(
            self.jobs,
            key=lambda j: (
                int(j.process_order) if int(j.process_order or 0) > 0 else 10**9,
                self.jobs.index(j),
            ),
        )
        for n, job in enumerate(ordered, start=1):
            job.process_order = n
            self._update_job_row(job)

    def _ordered_jobs(self) -> List[Job]:
        return sorted(
            self.jobs,
            key=lambda j: (
                int(j.process_order) if int(j.process_order or 0) > 0 else 10**9,
                self.jobs.index(j),
            ),
        )

    def _job_from_tree_id(self, tree_id: str) -> Optional[Job]:
        for job in self.jobs:
            if job.tree_id == tree_id:
                return job
        return None

    @staticmethod
    def _parse_hms_for_sort(value: str) -> float:
        s = str(value or "").strip()
        if not s or s in {"--", "PAUSED"}:
            return float("inf")
        try:
            parts = [float(x) for x in s.split(":")]
            if len(parts) == 3:
                return parts[0] * 3600.0 + parts[1] * 60.0 + parts[2]
            if len(parts) == 2:
                return parts[0] * 60.0 + parts[1]
            return float(parts[0])
        except Exception:
            return float("inf")

    def _queue_sort_key(self, job: Job, column: str):
        i = job.info

        if column == "order":
            return int(job.process_order or 0)
        if column == "file":
            return i.path.name.casefold()
        if column == "engine":
            return self._engine_display_name(self._job_settings_call(job, self._selected_engine)).casefold()
        if column == "factor":
            try:
                return float(self._job_settings_call(job, self._effective_ai_scale_for_estimate, i))
            except Exception:
                return 0.0
        if column == "source":
            return (int(i.width or 0) * int(i.height or 0), int(i.width or 0), int(i.height or 0))
        if column == "output_resolution":
            try:
                w, h, _fps, _factor = self._job_settings_call(job, self._output_geometry, i)
                if (job.verified_ai_output_width > 0 and job.verified_ai_output_height > 0
                        and job.status in ("Running", "Done")):
                    w, h = job.verified_ai_output_width, job.verified_ai_output_height
                return (int(w or 0) * int(h or 0), int(w or 0), int(h or 0))
            except Exception:
                return (0, 0, 0)
        if column == "fps_input":
            return float(i.fps or 0.0)
        if column == "fps_ai":
            try:
                return float(self._job_settings_call(job, self._fps_reduction_plan, i)[0] or 0.0)
            except Exception:
                return 0.0
        if column == "fps_output":
            try:
                return float(self._job_settings_call(job, self._output_geometry, i)[2] or 0.0)
            except Exception:
                return 0.0
        if column == "duration":
            return float(i.duration or 0.0)
        if column == "estimated":
            return (
                float(job.estimated_seconds)
                if job.estimated_seconds is not None
                else float("inf")
            )
        if column == "similarity":
            return int(job.estimate_similarity or 0)
        if column == "prediction_evidence":
            return str(job.prediction_evidence or "").casefold()
        if column == "elapsed":
            return float(job.elapsed_seconds or 0.0)
        if column == "bitrate":
            return self._predicted_bitrate_mbps(i, job)
        if column == "progress":
            return float(job.progress or 0.0)
        if column == "eta":
            return self._parse_hms_for_sort(job.eta)

        return ""

    def _sort_queue_table(
        self,
        column: str,
        reverse: Optional[bool] = None,
    ) -> None:
        if column not in getattr(self, "queue_columns", ()):
            return

        if reverse is None:
            if self._tree_sort_column == column:
                reverse = not bool(self._tree_sort_reverse)
            else:
                reverse = column in {"similarity"}

        self._tree_sort_column = column
        self._tree_sort_reverse = bool(reverse)

        jobs = sorted(
            self.jobs,
            key=lambda j: self._queue_sort_key(j, column),
            reverse=bool(reverse),
        )

        for position, job in enumerate(jobs):
            if job.tree_id and self.tree.exists(job.tree_id):
                self.tree.move(job.tree_id, "", position)


        for c in self.queue_columns:
            label = self._tree_titles.get(c, c)
            if c == column:
                label += " ▼" if reverse else " ▲"
            self.tree.heading(
                c,
                text=label,
                command=lambda col=c: self._sort_queue_table(col),
            )
        self.after_idle(self._refresh_factor_overlays)

    def _play_queue_file(self, job: Job) -> None:
        path = Path(job.info.path)
        if not path.is_file():
            messagebox.showerror(
                APP_NAME,
                f"The video file could not be found:\n\n{path}",
            )
            return
        try:
            if os.name == "nt":
                os.startfile(str(path))
            else:
                subprocess.Popen(["xdg-open", str(path)])
            self._log(f"V137 PLAY SOURCE: {path}")
        except Exception as e:
            messagebox.showerror(
                APP_NAME,
                f"Could not open the video with the system video player:\n\n{e}",
            )

    def _open_queue_cell_editor(self, job: Job, column_name: str) -> None:
        if self.worker and self.worker.is_alive():
            return
        if column_name not in {"order", "engine", "factor", "fps_ai"}:
            return
        if not job.tree_id or not self.tree.exists(job.tree_id):
            return
        try:
            column_id = f"#{self.queue_columns.index(column_name) + 1}"
        except Exception:
            return
        bbox = self.tree.bbox(job.tree_id, column_id)
        if not bbox:
            return
        x, y, width, height = bbox
        if self._order_editor is not None:
            try:
                self._order_editor.destroy()
            except Exception:
                pass
            self._order_editor = None
        if column_name == "factor":
            self._hide_factor_overlay(job)

        engine = self._job_settings_call(job, self._selected_engine)
        choice = self._job_settings_call(job, self._selected_upscale_choice, engine)
        if column_name == "engine":
            editor = ttk.Combobox(self.tree, values=("SeedVR2", "miniStarLight"), state="readonly", justify="center")
            editor.set(self._engine_display_name(engine))
        elif column_name == "factor":
            values = self._factor_editor_values(engine)
            editor = ttk.Combobox(self.tree, values=values, state="readonly", justify="center")
            target_resolution = self._job_settings_call(job, self._selected_seed_target_resolution) if engine == "SeedVR2" else "Use upscale factor"
            if engine == "SeedVR2" and target_resolution != "Use upscale factor" and not job.scale_choice_override:
                effective = self._planned_upscale_factor_text(job.info, job)
                effective_raw = str(effective).rstrip("Xx")
                if effective_raw in values:
                    editor.set(effective_raw)
                else:
                    editor.set(self._choice_to_editor_text(choice))
            else:
                editor.set(self._choice_to_editor_text(choice))
        else:
            editor = ttk.Entry(self.tree, justify="center")
            if column_name == "order":
                editor.insert(0, str(job.process_order))
            else:
                ai_fps = self._job_settings_call(job, self._fps_reduction_plan, job.info)[0]
                editor.insert(0, self._fmt_fps(ai_fps))
                editor.select_range(0, "end")

        editor.place(x=x, y=y, width=width, height=height)
        editor.focus_set()
        self._order_editor = editor
        committed = {"done": False}

        def close_editor():
            if self._order_editor is editor:
                self._order_editor = None
            try:
                editor.destroy()
            except Exception:
                pass
            self.after_idle(self._refresh_factor_overlays)

        def refresh_job():
            self._update_job_duration_estimate(job, force=True)
            self._update_job_row(job)
            self._refresh_preview()
            self.after_idle(self._refresh_factor_overlays)

        def commit(_event=None):
            if committed["done"]:
                return
            committed["done"] = True
            raw = editor.get().strip()

            if column_name == "order":
                try:
                    requested = int(raw)
                except Exception:
                    self.bell()
                    close_editor()
                    return
                requested = max(1, min(requested, max(1, len(self.jobs))))
                ordered = self._ordered_jobs()
                ordered = [j for j in ordered if j is not job]
                ordered.insert(requested - 1, job)
                for n, item in enumerate(ordered, start=1):
                    item.process_order = n
                    self._update_job_row(item)
                close_editor()
                return

            if column_name in ("engine", "factor"):
                close_editor()
                return

            if column_name == "fps_ai":
                if not raw:
                    job.ai_fps_override = 0.0
                    close_editor()
                    refresh_job()
                    return
                try:
                    target = float(raw.replace(",", "."))
                except Exception:
                    self.bell()
                    close_editor()
                    return
                if target <= 0:
                    self.bell()
                    close_editor()
                    return
                source_fps = float(job.info.fps or target)
                job.ai_fps_override = float(self._round_fps(min(target, source_fps)))
                self._initialize_job_section2_settings(job)
                job.section2_settings["fps_reduce_enable"] = True
                job.section2_settings["fps_reduce_mode"] = "Maximum FPS"
                job.section2_settings["fps_reduce_max"] = job.ai_fps_override
                close_editor()
                refresh_job()
                return

        def cancel(_event=None):
            if committed["done"]:
                return
            committed["done"] = True
            close_editor()

        editor.bind("<Return>", commit)
        editor.bind("<KP_Enter>", commit)
        editor.bind("<FocusOut>", commit)
        editor.bind("<Escape>", cancel)
        if isinstance(editor, ttk.Combobox):
            editor.bind("<<ComboboxSelected>>", commit)

    def _queue_single_click_order_edit(self, event) -> None:
        if self.worker and self.worker.is_alive():
            return
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        if not item_id or not column_id:
            return
        try:
            column_index = int(column_id.lstrip("#")) - 1
            column_name = self.queue_columns[column_index]
        except Exception:
            return
        if column_name != "order":
            return
        job = self._job_from_tree_id(item_id)
        if job is not None:
            self.after_idle(lambda j=job: self._open_queue_cell_editor(j, "order"))

    def _queue_double_click_view_only(self, event) -> None:
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        if not item_id or not column_id:
            return
        try:
            column_index = int(column_id.lstrip("#")) - 1
            column_name = self.queue_columns[column_index]
        except Exception:
            return
        job = self._job_from_tree_id(item_id)
        if job is None:
            return
        if column_name == "file":
            self._play_queue_file(job)
            return
        if column_name in {"order", "engine", "factor", "fps_ai"}:
            self._open_queue_cell_editor(job, column_name)

    def _begin_processing_order_edit(self, event) -> None:
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        if not item_id or not column_id:
            return
        try:
            column_index = int(column_id.lstrip("#")) - 1
            column_name = self.queue_columns[column_index]
        except Exception:
            return
        job = self._job_from_tree_id(item_id)
        if job is not None and column_name == "order":
            self._open_queue_cell_editor(job, "order")

    def _select_all_queue(self):
        if not hasattr(self, "tree"):
            return
        items = self.tree.get_children("")
        if not items:
            return
        self.tree.selection_set(items)
        try:
            self.tree.focus(items[0])
        except Exception:
            pass
        self._update_section2_selection_status()
        self.after_idle(self._refresh_factor_overlays)

    def _select_none_queue(self):
        if not hasattr(self, "tree"):
            return
        self.tree.selection_remove(self.tree.selection())
        self._update_section2_selection_status()
        self.after_idle(self._refresh_factor_overlays)

    def _delete_selected_movies(self):
        if self.worker and self.worker.is_alive():
            messagebox.showwarning(
                APP_NAME,
                "Movies cannot be deleted while the processing queue is running.",
                parent=self,
            )
            return

        selected_ids = list(self.tree.selection())
        if not selected_ids:
            messagebox.showinfo(
                APP_NAME,
                "Select one or more movies in Table #1 first.",
                parent=self,
            )
            return

        selected_jobs = [j for j in self.jobs if j.tree_id in set(selected_ids)]
        if not selected_jobs:
            return

        count = len(selected_jobs)
        noun = "file" if count == 1 else "files"
        confirmed = messagebox.askyesno(
            "Delete selected movies",
            f"Are you sure you want to permanently delete {count} {noun}?\n\n"
            "This deletes the movie file(s) from disk, not only from Table #1.",
            icon="warning",
            parent=self,
        )
        if not confirmed:
            return

        deleted_ids = set()
        failures = []

        for job in selected_jobs:
            source = Path(job.info.path)
            try:
                if source.is_file():
                    source.unlink()
                    deleted_ids.add(job.tree_id)
                    self._post("log", f"DELETED SOURCE MOVIE: {source}")
                else:
                    failures.append(f"{source} — file not found")
            except Exception as e:
                failures.append(f"{source} — {e}")

        if deleted_ids:
            self.jobs = [j for j in self.jobs if j.tree_id not in deleted_ids]
            for tree_id in deleted_ids:
                if self.tree.exists(tree_id):
                    self.tree.delete(tree_id)
            self._normalize_processing_order()
            self._sort_queue_table(
                self._tree_sort_column,
                reverse=self._tree_sort_reverse,
            )
            self._update_dynamic_path_preview()
            self._update_total_queue_estimate()
            self._refresh_preview()

        if failures:
            preview = "\n".join(failures[:8])
            if len(failures) > 8:
                preview += f"\n... and {len(failures) - 8} more"
            messagebox.showwarning(
                "Some movies were not deleted",
                f"Deleted {len(deleted_ids)} of {count} selected {noun}.\n\n"
                f"Could not delete:\n{preview}",
                parent=self,
            )

    def _remove_selected(self):
        if self.worker and self.worker.is_alive():
            return
        selected = set(self.tree.selection())
        if not selected:
            return
        self.jobs = [j for j in self.jobs if j.tree_id not in selected]
        for x in selected:
            self.tree.delete(x)
        self._normalize_processing_order()
        self._sort_queue_table(
            self._tree_sort_column,
            reverse=self._tree_sort_reverse,
        )
        self._update_dynamic_path_preview()
        self._update_total_queue_estimate()
        self._refresh_preview()

    def _clear_queue(self):
        if self.worker and self.worker.is_alive():
            return
        self.jobs.clear()
        for x in self.tree.get_children():
            self.tree.delete(x)
        self._update_dynamic_path_preview()
        self._update_total_queue_estimate()
        self._refresh_preview()


    def _ensure_duration_history_file(self) -> None:
        try:
            with self._duration_history_lock:
                self.duration_history_path.parent.mkdir(parents=True, exist_ok=True)
                if not self.duration_history_path.is_file() or self.duration_history_path.stat().st_size == 0:
                    with self.duration_history_path.open("w", encoding="utf-8-sig", newline="") as fh:
                        csv.DictWriter(fh, fieldnames=DURATION_HISTORY_COLUMNS).writeheader()
                    return

                with self.duration_history_path.open("r", encoding="utf-8-sig", newline="") as fh:
                    reader = csv.DictReader(fh)
                    old_fields = list(reader.fieldnames or [])
                    old_rows = [dict(r) for r in reader if isinstance(r, dict)]

                if all(k in old_fields for k in DURATION_HISTORY_COLUMNS):
                    return

                # Preserve the complete, original historical data before adding new blank columns.
                backup = self.duration_history_path.with_name("Upscaler_duration_history_before_V251.csv")
                if not backup.exists():
                    shutil.copy2(self.duration_history_path, backup)
                tmp = self.duration_history_path.with_suffix(self.duration_history_path.suffix + ".migrate.tmp")
                with tmp.open("w", encoding="utf-8-sig", newline="") as fh:
                    upgraded_fields = list(dict.fromkeys(DURATION_HISTORY_COLUMNS + old_fields))
                    writer = csv.DictWriter(fh, fieldnames=upgraded_fields, extrasaction="ignore")
                    writer.writeheader()
                    for row in old_rows:
                        writer.writerow({k: row.get(k, "") for k in upgraded_fields})
                os.replace(tmp, self.duration_history_path)
        except Exception:

            pass

    def _seed_start_benchmark_sampler(self):
        """Non-blocking GPU sampling; approximate maxima, not exact hardware peaks."""
        end = threading.Event()
        measurements = {"max_dedicated": 0.0, "max_shared": 0.0,
                        "gpu_sum": 0.0, "gpu_count": 0}

        def sample():
            while not end.is_set():
                try:
                    stats = self._read_nvidia_stats()
                    if stats is not None:
                        util, dedicated_mib, _total_mib = stats
                        measurements["max_dedicated"] = max(
                            measurements["max_dedicated"], float(dedicated_mib) / 1024.0)
                        measurements["gpu_sum"] += float(util)
                        measurements["gpu_count"] += 1
                    shared = self._spill_mib  # Existing UI monitoring; no extra PowerShell processes.
                    if shared is not None:
                        measurements["max_shared"] = max(
                            measurements["max_shared"], float(shared) / 1024.0)
                except Exception:
                    pass
                end.wait(3.0)

        worker = threading.Thread(target=sample, daemon=True, name="SeedVR2-benchmark-sampler")
        worker.start()
        return end, worker, measurements

    def _record_seed_benchmark_attempt(self, job: Job, attempt_number: int, batch: int,
                                       overlap: int, scale: float, duration: float,
                                       status: str, error_text: str, samples: Dict[str, Any]) -> None:
        try:
            ai = job.ai_info or job.info
            if not job.seed_benchmark_run_id:
                job.seed_benchmark_run_id = uuid.uuid4().hex
            source_id = job.history_source_sha256 or self._v248_source_fingerprint(job.info.path)
            model_id = job.history_seed_model_id or self._v248_checkpoint_digest("workflow_json", self.workflow_json)
            prompt_times = list(self._seed_batch_times)
            estimated_batches = int(job.seed_expected_batches or 0)
            # LongVideo prints Meta-Batch 1/N ... (N-1)/N before its final prompt.
            # The number of completed prompt-timing events is the better final count.
            observed_batches = max(int(self._seed_last_meta_batch or 0), len(prompt_times))
            requested = job.seed_initial_batch_requested or "Auto"
            requested_overlap = job.seed_initial_overlap_requested or "Auto"
            requested_tile = job.seed_initial_vae_tile_requested or "Auto"
            requested_spatial = job.seed_initial_vae_overlap_requested or "Auto"
            count = max(0, int(ai.frames or 0))
            now = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
            maximum = max(0.0, float(samples.get("max_dedicated", 0.0) or 0.0))
            shared = max(0.0, float(samples.get("max_shared", 0.0) or 0.0))
            job.seed_peak_dedicated_vram_gb = max(job.seed_peak_dedicated_vram_gb, maximum)
            job.seed_peak_shared_gpu_gb = max(job.seed_peak_shared_gpu_gb, shared)
            sample_count = max(0, int(samples.get("gpu_count", 0) or 0))
            launch, disable_dvram, disable_async = self._comfy_launch_signature()
            row = {
                "run_id": job.seed_benchmark_run_id,
                "attempt_id": f"{job.seed_benchmark_run_id}-{attempt_number:02d}",
                "datetime_local": now, "app_version": SERIAL_VERSION, "result": status,
                "source_content_sha256": source_id,
                "workflow_model_identifier": model_id,
                "configuration_sha256": str(job.history_configuration_sha256 or ""),
                "source_resolution": f"{job.info.width}x{job.info.height}",
                "source_fps": f"{job.info.fps:.6f}",
                "source_frames": str(int(job.info.frames or 0)),
                "source_duration_seconds": f"{float(job.info.duration or 0.0):.6f}",
                "ai_input_resolution": f"{ai.width}x{ai.height}",
                "ai_input_fps": f"{ai.fps:.6f}",
                "ai_input_frames": str(count),
                "ai_output_width": str(int(round(ai.width * scale))),
                "ai_output_height": str(int(round(ai.height * scale))),
                "seedvr2_factor": f"{scale:.6f}",
                "requested_max_temporal_batch": requested,
                "requested_temporal_overlap": requested_overlap,
                "requested_vae_tile": requested_tile,
                "requested_vae_spatial_overlap": requested_spatial,
                "effective_temporal_batch": str(int(batch)),
                "effective_temporal_overlap": str(int(overlap)),
                "vae_tile_pixels": str(int(job.seed_vae_tile_used)) if job.seed_vae_tile_used else "",
                "vae_spatial_overlap_pixels": (
                    str(int(job.seed_vae_spatial_overlap_used)) if job.seed_vae_tile_used > 0 else ""),
                "estimated_meta_batches": str(estimated_batches),
                "observed_meta_batches": str(observed_batches),
                "attempt_index": str(int(attempt_number)),
                "attempt_elapsed_seconds": f"{duration:.6f}",
                "attempt_effective_fps": (f"{count / duration:.6f}"
                                          if status == "SUCCESS" and duration > 0 and count else ""),
                "comfy_prompt_elapsed_seconds_sum": f"{sum(prompt_times):.6f}" if prompt_times else "",
                "comfy_prompt_timing_events": str(len(prompt_times)),
                "gpu_utilization_percent_mean_sampled": (
                    f"{float(samples.get('gpu_sum', 0.0)) / sample_count:.3f}" if sample_count else ""),
                "peak_dedicated_vram_gb_sampled": f"{maximum:.3f}" if sample_count else "",
                "peak_shared_gpu_gb_sampled": f"{shared:.3f}" if shared else "",
                "sampled_gpu_count": str(sample_count),
                "nvidia_launch_mode": launch,
                "dynamic_vram_enabled": "0" if disable_dvram else "1",
                "async_offload_enabled": "0" if disable_async else "1",
                "error_detail": str(error_text or "")[:800].replace("\r", " ").replace("\n", " "),
            }

            now_dt = _dt.datetime.now().astimezone()
            attempt_row = {
                "movie_id": f"SEED_ATTEMPT_{row['attempt_id']}",
                "date_local": now_dt.strftime("%Y-%m-%d"),
                "day_local": now_dt.strftime("%A"),
                "time_local": now_dt.strftime("%H:%M:%S"),
                "history_schema_version": "V252-attempt",
                "record_type": "SEED_ATTEMPT",
                "algorithm": "SeedVR2",
                "algorithm_mode": "SeedVR2 attempt; not a completed movie",
                "source_content_sha256": row["source_content_sha256"],
                "configuration_sha256": row["configuration_sha256"],
                "seed_model_identifier": row["workflow_model_identifier"],
                "source_resolution": row["source_resolution"],
                "source_width": str(job.info.width),
                "source_height": str(job.info.height),
                "source_fps": row["source_fps"],
                "source_frames": row["source_frames"],
                "movie_length_seconds": row["source_duration_seconds"],
                "ai_input_fps": row["ai_input_fps"],
                "ai_input_frames": row["ai_input_frames"],
                "ai_output_width": row["ai_output_width"],
                "ai_output_height": row["ai_output_height"],
                "ai_output_resolution": f"{row['ai_output_width']}x{row['ai_output_height']}",
                "scale_factor": row["seedvr2_factor"],
                "seedvr2_factor": row["seedvr2_factor"],
                "seed_frames_per_batch": row["effective_temporal_batch"],
                "seed_overlap": row["effective_temporal_overlap"],
                "seed_expected_meta_batches": row["estimated_meta_batches"],
                "seed_requested_max_temporal_batch": row["requested_max_temporal_batch"],
                "seed_requested_temporal_overlap": row["requested_temporal_overlap"],
                "seed_vae_tile_pixels": row["vae_tile_pixels"],
                "seed_vae_spatial_overlap_pixels": row["vae_spatial_overlap_pixels"],
                "seed_requested_vae_tile": row["requested_vae_tile"],
                "seed_requested_vae_spatial_overlap": row["requested_vae_spatial_overlap"],
                "seed_peak_dedicated_vram_gb_sampled": row["peak_dedicated_vram_gb_sampled"],
                "seed_peak_shared_gpu_gb_sampled": row["peak_shared_gpu_gb_sampled"],
                "seed_nvidia_launch_mode": row["nvidia_launch_mode"],
                "seed_disable_dynamic_vram": "0" if row["dynamic_vram_enabled"] == "1" else "1",
                "seed_disable_async_offload": "0" if row["async_offload_enabled"] == "1" else "1",
                "seed_dynamic_vram_enabled": row["dynamic_vram_enabled"],
                "seed_async_offload_enabled": row["async_offload_enabled"],
                "seed_attention_backend_reported": "ComfyUI PyTorch attention; CUDA SDPA kernel unverified",
                "seed_blockswap_status": "unavailable in legacy LongVideo workflow",
                "seed_dit_compile_status": "unavailable in legacy LongVideo workflow",
                "seed_run_id": row["run_id"],
                "seed_attempt_id": row["attempt_id"],
                "seed_attempt_index": row["attempt_index"],
                "seed_attempt_result": row["result"],
                "seed_attempt_elapsed_seconds": row["attempt_elapsed_seconds"],
                "seed_attempt_effective_fps": row["attempt_effective_fps"],
                "seed_observed_meta_batches": row["observed_meta_batches"],
                "seed_comfy_prompt_elapsed_seconds_sum": row["comfy_prompt_elapsed_seconds_sum"],
                "seed_comfy_prompt_timing_events": row["comfy_prompt_timing_events"],
                "seed_gpu_utilization_percent_mean_sampled": row["gpu_utilization_percent_mean_sampled"],
                "seed_gpu_samples_count": row["sampled_gpu_count"],
                "seed_requested_batch_at_attempt": str(batch),
                "seed_requested_overlap_at_attempt": str(overlap),
                "seed_attempt_error_detail": row["error_detail"],
            }
            with self._duration_history_lock:
                self._ensure_duration_history_file()
                with self.duration_history_path.open("r", encoding="utf-8-sig", newline="") as fh:
                    fields = list(csv.DictReader(fh).fieldnames or DURATION_HISTORY_COLUMNS)
                with self.duration_history_path.open("a", encoding="utf-8-sig", newline="") as fh:
                    csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore").writerow(attempt_row)
                    fh.flush()
                    try:
                        os.fsync(fh.fileno())
                    except OSError:
                        pass
            self._invalidate_duration_history_cache()
            self._post("log", f"V255 SEEDVR2 ATTEMPT: {status}; temporal batch={batch}; "
                              f"VAE tile={job.seed_vae_tile_used}; elapsed={duration:.1f}s; "
                              f"dedicated VRAM peak={maximum:.2f} GB (sampled); "
                              f"history={self.duration_history_path}")
        except Exception as exc:
            self._post("log", f"V250 benchmark logging warning: {exc}")

    @staticmethod
    def _history_float(row: Dict[str, str], key: str, default: float = 0.0) -> float:
        try:
            return float(row.get(key, default) or default)
        except Exception:
            return float(default)

    @staticmethod
    def _safe_log_ratio(a: float, b: float) -> float:
        a = max(1e-12, float(a))
        b = max(1e-12, float(b))
        try:
            return abs(math.log(a / b, 2.0))
        except Exception:
            return 0.0

    @staticmethod
    def _history_bool(row: Dict[str, str], key: str, default: bool = False) -> bool:
        raw = str(row.get(key, "") or "").strip().lower()
        if not raw:
            return bool(default)
        return raw in {"1", "true", "yes", "on"}

    def _load_duration_history(self, force: bool = False) -> List[Dict[str, str]]:
        self._ensure_duration_history_file()
        try:
            with self._duration_history_lock:
                mtime_ns = self.duration_history_path.stat().st_mtime_ns
                if (
                    not force
                    and self._duration_history_cache is not None
                    and self._duration_history_cache_mtime_ns == mtime_ns
                ):
                    return list(self._duration_history_cache)

                rows: List[Dict[str, str]] = []
                with self.duration_history_path.open("r", encoding="utf-8-sig", newline="") as fh:
                    reader = csv.DictReader(fh)
                    for row in reader:
                        if not isinstance(row, dict):
                            continue
                        if str(row.get("record_type", "") or "").upper() == "SEED_ATTEMPT":
                            continue  # Never allow incomplete attempts to trains ETA !!!!!.
                        runtime = self._history_float(row, "processing_duration_seconds")
                        length = self._history_float(row, "movie_length_seconds")
                        width = self._history_float(row, "source_width")
                        height = self._history_float(row, "source_height")
                        scale = self._history_float(row, "scale_factor")
                        algorithm = str(row.get("algorithm", "") or "").strip()
                        if runtime > 0 and length > 0 and width > 0 and height > 0 and scale > 0 and algorithm:
                            rows.append(dict(row))

                self._duration_history_cache = rows
                self._duration_history_cache_mtime_ns = mtime_ns
                return list(rows)
        except Exception:
            return []

    def _invalidate_duration_history_cache(self) -> None:
        with self._duration_history_lock:
            self._duration_history_cache = None
            self._duration_history_cache_mtime_ns = None

    def _algorithm_for_estimate(self, engine: Optional[str] = None) -> str:
        return "SeedVR2"


    def _rife_multiplier_int(self) -> int:
        raw = self._selected_rife_multiplier()
        try:
            value = int(str(raw).upper().replace("X", ""))
        except Exception:
            value = 2
        return value if value in RIFE_MULTIPLIERS else 2

    def _selected_fps_reduce_enable(self) -> bool:
        ctx = self._job_settings_context
        if isinstance(ctx, Job) and float(ctx.ai_fps_override or 0.0) > 0:
            return True
        if isinstance(ctx, Job):
            return bool(self._job_setting("fps_reduce_enable", self.fps_reduce_enable))
        if self._run_engine is not None and self._run_fps_reduce_enable is not None:
            return bool(self._run_fps_reduce_enable)
        return bool(self._job_setting("fps_reduce_enable", self.fps_reduce_enable))

    def _selected_fps_reduce_mode(self) -> str:
        return "Maximum FPS"

    def _selected_fps_reduce_max(self) -> float:
        ctx = self._job_settings_context
        if isinstance(ctx, Job) and float(ctx.ai_fps_override or 0.0) > 0:
            raw = float(self._round_fps(ctx.ai_fps_override))
        elif isinstance(ctx, Job):
            try:
                raw = float(self._round_fps(self._job_setting("fps_reduce_max", self.fps_reduce_max)))
            except Exception:
                raw = 30.0
        elif self._run_engine is not None and self._run_fps_reduce_max is not None:
            raw = float(self._round_fps(self._run_fps_reduce_max))
        else:
            try:
                raw = float(self._round_fps(self._job_setting("fps_reduce_max", self.fps_reduce_max)))
            except Exception:
                raw = 30.0

        allowed = [float(x) for x in FPS_MAX_FOR_AI_CHOICES]
        return min(allowed, key=lambda x: abs(x - raw))

    def _update_rife_controls(self) -> None:
        if not hasattr(self, "rife_multiplier_box") or not hasattr(self, "rife_target_spin"):
            return
        enabled = bool(self._job_setting("rife_enable", self.rife_enable))
        mode = self._job_setting("rife_mode", self.rife_mode) if self._job_setting("rife_mode", self.rife_mode) in RIFE_MODES else "Multiplier"
        if not enabled:
            self.rife_multiplier_box.configure(state="disabled")
            self.rife_target_spin.configure(state="disabled")
        elif mode == "Multiplier":
            self.rife_multiplier_box.configure(state="readonly")
            self.rife_target_spin.configure(state="disabled")
        else:
            self.rife_multiplier_box.configure(state="disabled")
            self.rife_target_spin.configure(state="normal")

    def _selected_rife_enable(self) -> bool:
        if isinstance(self._job_settings_context, Job):
            return bool(self._job_setting("rife_enable", self.rife_enable))
        if self._run_engine is not None and self._run_rife_enable is not None:
            return bool(self._run_rife_enable)
        return bool(self._job_setting("rife_enable", self.rife_enable))

    def _selected_rife_mode(self) -> str:
        if isinstance(self._job_settings_context, Job):
            raw = str(self._job_setting("rife_mode", self.rife_mode))
            return raw if raw in RIFE_MODES else "Multiplier"
        if self._run_engine is not None and self._run_rife_mode in RIFE_MODES:
            return str(self._run_rife_mode)
        raw = self._job_setting("rife_mode", self.rife_mode)
        return raw if raw in RIFE_MODES else "Multiplier"

    def _selected_rife_multiplier(self) -> str:
        allowed = {f"{x}X" for x in RIFE_MULTIPLIERS}
        if isinstance(self._job_settings_context, Job):
            raw = str(self._job_setting("rife_multiplier", self.rife_multiplier))
            return raw if raw in allowed else "2X"
        if self._run_engine is not None and self._run_rife_multiplier in allowed:
            return str(self._run_rife_multiplier)
        raw = self._job_setting("rife_multiplier", self.rife_multiplier)
        return raw if raw in allowed else "2X"

    def _selected_rife_target_fps(self) -> float:
        if isinstance(self._job_settings_context, Job):
            try:
                return float(self._round_fps(self._job_setting("rife_target_fps", self.rife_target_fps)))
            except Exception:
                return 50.0
        if self._run_engine is not None and self._run_rife_target_fps is not None:
            return float(self._round_fps(self._run_rife_target_fps))
        try:
            return float(self._round_fps(self._job_setting("rife_target_fps", self.rife_target_fps)))
        except Exception:
            return 50.0

    def _rife_factor_chain_for_fps(self, ai_fps: float) -> List[int]:
        ai_fps = float(self._round_fps(ai_fps))
        if not self._selected_rife_enable() or ai_fps <= 0:
            return []

        if self._selected_rife_mode() == "Multiplier":
            return [self._rife_multiplier_int()]

        target = float(self._round_fps(self._selected_rife_target_fps()))
        if target <= ai_fps:
            return []

        required = target / ai_fps
        frontier: Dict[int, List[int]] = {1: []}
        for _pass_index in range(1, 17):
            next_frontier: Dict[int, List[int]] = {}
            candidates: List[Tuple[int, int, List[int]]] = []
            for product, chain in frontier.items():
                for factor in RIFE_MULTIPLIERS:
                    new_product = int(product * factor)
                    new_chain = chain + [int(factor)]
                    if new_product + 1e-12 >= required:
                        candidates.append((new_product, len(new_chain), new_chain))
                    elif new_product not in next_frontier:
                        next_frontier[new_product] = new_chain
            if candidates:
                candidates.sort(key=lambda item: (item[0], item[1], item[2]))
                return candidates[0][2]
            frontier = next_frontier
            if not frontier:
                break
        raise BackendError(
            f"Unable to build a RIFE interpolation chain for {ai_fps:g} FPS -> {target:g} FPS."
        )

    def _rife_plan_for_fps(self, ai_fps: float) -> Tuple[bool, int, float]:
        ai_fps = float(self._round_fps(ai_fps))
        if not self._selected_rife_enable() or ai_fps <= 0:
            return False, 1, ai_fps

        if self._selected_rife_mode() == "Multiplier":
            mult = self._rife_multiplier_int()
            return True, mult, float(self._round_fps(ai_fps * mult))

        target = float(self._round_fps(self._selected_rife_target_fps()))
        if target <= ai_fps:
            return False, 1, target

        chain = self._rife_factor_chain_for_fps(ai_fps)
        total_multiplier = 1
        for factor in chain:
            total_multiplier *= int(factor)
        return True, int(total_multiplier), target

    def _fps_reduction_plan(self, info: VideoInfo) -> Tuple[float, str, float, bool]:
        source_fps = float(self._round_fps(info.fps))
        if source_fps <= 0:
            return 0.0, "Off", 0.0, False
        if not self._selected_fps_reduce_enable():
            return source_fps, "Off", 0.0, False

        value = self._selected_fps_reduce_max()
        target = min(source_fps, value)
        target = float(self._round_fps(max(1.0, target)))
        applied = target < source_fps
        return (target if applied else source_fps), "Maximum FPS", float(value), applied

    def _effective_ai_scale_for_estimate(
        self, info: VideoInfo, engine: Optional[str] = None,
        choice: Optional[str] = None,
    ) -> float:
        if not self._selected_upscale_enable():
            return 1.0
        engine = engine or self._selected_engine()
        return float(max(1.0, self._factor_for(info, engine, choice)))

    def _planned_ai_output_geometry(self, info: VideoInfo) -> Tuple[int, int]:
        """Use the SAME geometry as the actual runtime pipeline."""
        if not self._selected_upscale_enable():
            effective = self._effective_upscale_info(info)
            return effective.width, effective.height
        w, h, _fps, _factor = self._output_geometry(info)
        return w, h

    def _duration_estimation_features(self, info: VideoInfo) -> Dict[str, Any]:
        ai_source_info = self._effective_upscale_info(info)
        engine = self._selected_engine()
        choice = self._selected_upscale_choice(engine)
        algorithm = self._algorithm_for_estimate(engine)
        scale = self._effective_ai_scale_for_estimate(ai_source_info, engine, choice)
        ai_fps, reduce_mode, reduce_value, reduced = self._fps_reduction_plan(info)
        length = max(0.001, float(info.duration or 0.001))
        source_pixels = max(1.0, float(max(1, info.width) * max(1, info.height)))

        ai_w, ai_h = self._planned_ai_output_geometry(ai_source_info)
        ai_pixels = max(1.0, float(max(1, ai_w) * max(1, ai_h)))
        ai_pixel_rate = ai_pixels * max(1e-6, ai_fps)
        workload = ai_pixel_rate * length
        ai_frames = max(1, int(round(length * max(1e-6, ai_fps))))

        # Neural restoration at 1X is still an expensive AI inference pass.
        # This flag records whether the engine RUNS, not whether dimensions grow.
        upscale_used = bool(self._selected_upscale_enable())

        rife_used, rife_mult, rife_out_fps = self._rife_plan_for_fps(ai_fps)
        rife_input_frames = int(ai_frames)
        rife_output_fps = float(self._round_fps(rife_out_fps if self._selected_rife_enable() else ai_fps))
        rife_output_frames = max(1, int(round(length * max(1e-6, rife_output_fps))))
        if rife_used and self._selected_rife_mode() == "Target FPS":
            rife_raw_output_fps = float(self._round_fps(rife_output_fps))
        else:
            rife_raw_output_fps = float(self._round_fps(ai_fps * rife_mult)) if rife_used else float(self._round_fps(ai_fps))
        rife_raw_output_frames = max(1, int(round(length * max(1e-6, rife_raw_output_fps))))
        rife_generated_frames = max(0, rife_raw_output_frames - rife_input_frames) if rife_used else 0
        rife_pixels = float(ai_pixels)
        rife_generated_pixel_frames = rife_pixels * float(rife_generated_frames)

        seed_batch = 0
        seed_overlap = 0
        seed_batches = 0
        if engine == "SeedVR2":
            synthetic = VideoInfo(
                path=info.path,
                width=ai_source_info.width,
                height=ai_source_info.height,
                fps=ai_fps,
                duration=length,
                frames=ai_frames,
            )
            manual_batch, manual_overlap, _tile, _spatial = self._seed_user_controls()
            seed_batch, auto_overlap = self._auto_seed_temporal_params(
                synthetic, max(1.0, self._factor_for(ai_source_info, engine, choice)), manual_batch
            )
            seed_overlap = int(manual_overlap if manual_overlap is not None else auto_overlap)
            seed_batches = int(math.ceil(ai_frames / max(1, seed_batch)))

        try:
            file_size = max(0, int(info.path.stat().st_size))
        except Exception:
            file_size = 0

        final_w, final_h, final_fps, _factor = self._output_geometry(info)
        final_encode_pixel_frames = (
            float(max(1, final_w))
            * float(max(1, final_h))
            * float(max(1, int(round(length * max(1e-6, final_fps)))))
        )
        rife_pipeline_workload = (
            rife_generated_pixel_frames + final_encode_pixel_frames
            if rife_used else 0.0
        )
        source_decode_workload = source_pixels * max(1.0, float(self._round_fps(info.fps))) * length
        pre_ai_workload = source_pixels * max(1.0, float(self._round_fps(ai_fps))) * length
        enhancement_workload = ai_pixels * max(1.0, float(self._round_fps(ai_fps))) * length
        comfy_mode, comfy_disable_dynamic, comfy_disable_async = self._comfy_launch_signature()
        ctx = self._job_settings_context
        iterative_used = False
        iterative_plan_id = ""
        iterative_ai_passes = 0
        iterative_target_factor = 0.0
        return {
            "algorithm": algorithm,
            "mode": str(choice),
            "preseed_mode": self._selected_preseed_mode() if engine == "SeedVR2" else "Only Bicubic",
            "pre_neural_downscale_factor": (self._selected_pre_neural_downscale_factor() if engine == "SeedVR2" and self._selected_preseed_mode() != "Only Bicubic" else 1.0),
            "pre_neural_input_pixels": (float(math.prod(self._pre_neural_source_dimensions(ai_source_info)[:2])) if engine == "SeedVR2" and self._selected_preseed_mode() != "Only Bicubic" else float(max(1,ai_source_info.width*ai_source_info.height))),
            "preseed_factor": (self._selected_native_preseed_factor(ai_source_info) if engine == "SeedVR2" else 1.0),
            "seedvr2_factor": (self._selected_preseed_seed_factor(ai_source_info) if engine == "SeedVR2" else 1.0),
            "scale": float(scale),
            "file_size": float(file_size),
            "length": length,
            "source_w": int(info.width or 0),
            "source_h": int(info.height or 0),
            "source_fps": float(self._round_fps(info.fps)),
            "source_pixels": source_pixels,
            "reduce_enabled": bool(reduced),
            "reduce_mode": reduce_mode if reduced else "Off",
            "reduce_value": float(reduce_value if reduced else 0.0),
            "ai_fps": float(self._round_fps(ai_fps)),
            "ai_frames": int(ai_frames),
            "ai_w": int(ai_w),
            "ai_h": int(ai_h),
            "ai_pixels": ai_pixels,
            "ai_pixel_rate": ai_pixel_rate,
            "workload": max(1.0, workload),
            "upscale_used": bool(upscale_used),
            "seed_batch": int(seed_batch),
            "seed_overlap": int(seed_overlap),
            "seed_batches": int(seed_batches),
            "rife_used": rife_used,
            "rife_multiplier": int(rife_mult),
            "rife_gpu_threads": RIFE_GPU_THREADS_FIXED if rife_used else 0,
            "rife_input_fps": float(self._round_fps(ai_fps)),
            "rife_output_fps": rife_output_fps,
            "rife_input_frames": int(rife_input_frames),
            "rife_output_frames": int(rife_output_frames),
            "rife_generated_frames": int(rife_generated_frames),
            "rife_pixels": float(rife_pixels),
            "rife_generated_pixel_frames": max(0.0, float(rife_generated_pixel_frames)),
            "final_encode_pixel_frames": max(1.0, float(final_encode_pixel_frames)),
            "final_encoder": self._selected_encode_backend(),
            "final_quality": self._selected_encode_quality(),
            "final_quality_value": (
                NVENC_CQ_VALUES[self._selected_encode_quality()]
                if self._selected_encode_backend() == "NVIDIA NVENC (fast)"
                else X265_CRF_VALUES[self._selected_encode_quality()]
            ),
            "final_encoder_threads": (
                0 if self._selected_encode_backend() == "NVIDIA NVENC (fast)" else self._selected_x265_threads()
            ),
            "expected_bitrate_mbps": self._quality_bitrate(final_w, final_h, final_fps),
            "rife_pipeline_workload": max(0.0, float(rife_pipeline_workload)),
            "source_decode_workload": max(1.0, float(source_decode_workload)),
            "pre_ai_workload": max(1.0, float(pre_ai_workload)),
            "enhancement_workload": max(1.0, float(enhancement_workload)),
            "repair": self._enhancement_is_enabled() and bool(self._job_setting("repair_enable", self.repair_enable)),
            "seed_nvidia_launch_mode": comfy_mode if engine == "SeedVR2" else "",
            "seed_disable_dynamic_vram": bool(comfy_disable_dynamic) if engine == "SeedVR2" else False,
            "seed_disable_async_offload": bool(comfy_disable_async) if engine == "SeedVR2" else False,
            "denoise": str(self._job_setting("denoise", self.denoise)) if self._enhancement_is_enabled() else "Off",
            "color": str(self._job_setting("color_correction", self.color_correction)) if self._enhancement_is_enabled() else "Off",
            "brightness": str(self._job_setting("brightness_correction", self.brightness_correction)) if self._enhancement_is_enabled() else "Off",
            "white": str(self._job_setting("white_correction", self.white_correction)) if self._enhancement_is_enabled() else "Off",
            "iterative_used": bool(iterative_used),
            "iterative_plan_id": iterative_plan_id,
            "iterative_target_factor": float(iterative_target_factor),
            "iterative_ai_passes": int(iterative_ai_passes),
            "out_w": int(final_w or 0),
            "out_h": int(final_h or 0),
            "out_fps": float(final_fps or 0.0),
        }

    def _history_estimation_features(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        runtime = self._history_float(row, "processing_duration_seconds")
        length = self._history_float(row, "movie_length_seconds")
        sw = int(round(self._history_float(row, "source_width")))
        sh = int(round(self._history_float(row, "source_height")))
        source_fps = float(self._round_fps(self._history_float(row, "source_fps")))
        scale = self._history_float(row, "scale_factor", 1.0)
        algorithm = str(row.get("algorithm", "") or "").strip()
        mode = str(row.get("algorithm_mode", "") or "").strip()
        if runtime <= 0 or length <= 0 or sw <= 0 or sh <= 0 or scale <= 0 or not algorithm:
            return None

        ai_fps = float(self._round_fps(self._history_float(row, "ai_input_fps", source_fps)))
        if ai_fps <= 0:
            ai_fps = source_fps if source_fps > 0 else 30.0
        ai_frames = int(round(self._history_float(row, "ai_input_frames", length * ai_fps)))

        ai_w = int(round(self._history_float(row, "ai_output_width")))
        ai_h = int(round(self._history_float(row, "ai_output_height")))
        if ai_w <= 0 or ai_h <= 0:
            if ai_w <= 0 or ai_h <= 0:
                ai_w = self._even_dimension(sw * scale)
                ai_h = self._even_dimension(sh * scale)


        ai_pixels = self._history_float(row, "ai_output_pixels_per_frame", ai_w * ai_h)
        ai_pixel_rate = self._history_float(row, "ai_pixel_rate", ai_pixels * ai_fps)
        workload = self._history_float(row, "ai_workload_pixel_frames", ai_pixel_rate * length)
        if workload <= 0:
            workload = max(1.0, ai_pixels * ai_fps * length)

        reduce_mode = str(row.get("fps_reduce_mode", "") or "").strip() or "Off"
        reduce_enabled = self._history_bool(row, "fps_reduce_enabled", reduce_mode != "Off")
        reduce_value = self._history_float(row, "fps_reduce_value", 0.0)

        rife_used = self._history_bool(row, "rife_used", False)
        rife_multiplier = max(1, int(round(self._history_float(row, "rife_multiplier", 2.0 if rife_used else 1.0))))
        rife_gpu_threads = int(round(self._history_float(row, "rife_gpu_threads", 0.0))) if rife_used else 0
        rife_input_fps = float(self._round_fps(self._history_float(row, "rife_input_fps", ai_fps)))
        if rife_input_fps <= 0:
            rife_input_fps = ai_fps
        default_rife_output_fps = rife_input_fps * rife_multiplier if rife_used else rife_input_fps
        rife_output_fps = float(self._round_fps(self._history_float(row, "rife_output_fps", default_rife_output_fps)))
        rife_input_frames = int(round(self._history_float(row, "rife_input_frames", ai_frames)))
        rife_output_frames = int(round(self._history_float(row, "rife_output_frames", length * rife_output_fps)))
        rife_raw_output_frames = int(round(length * max(1e-6, rife_input_fps * rife_multiplier))) if rife_used else rife_input_frames
        rife_generated_frames = int(round(self._history_float(row, "rife_generated_frames", max(0, rife_raw_output_frames - rife_input_frames)))) if rife_used else 0
        rife_pixels = self._history_float(row, "rife_pixels_per_frame", ai_pixels)
        rife_generated_pixel_frames = self._history_float(
            row,
            "rife_generated_pixel_frames",
            max(0.0, rife_pixels * rife_generated_frames),
        )
        output_w = int(round(self._history_float(row, "output_width", ai_w)))
        output_h = int(round(self._history_float(row, "output_height", ai_h)))
        final_encode_pixel_frames = self._history_float(
            row,
            "final_encode_pixel_frames",
            max(1.0, output_w * output_h * max(1, rife_output_frames if rife_used else ai_frames)),
        )
        rife_pipeline_workload = self._history_float(
            row,
            "rife_pipeline_workload",
            rife_generated_pixel_frames + final_encode_pixel_frames if rife_used else 0.0,
        )
        source_decode_workload = max(1.0, float(sw * sh) * max(1.0, source_fps) * length)
        pre_ai_workload = max(1.0, float(sw * sh) * max(1.0, ai_fps) * length)
        enhancement_workload = max(1.0, ai_pixels * max(1.0, ai_fps) * length)
        seed_nvidia_launch_mode = str(row.get("seed_nvidia_launch_mode", "") or "").strip()
        seed_disable_dynamic_vram = self._history_bool(row, "seed_disable_dynamic_vram", False)
        seed_disable_async_offload = self._history_bool(row, "seed_disable_async_offload", False)
        inferred_upscale_used = (
            self._history_float(row, "stage_ai_seconds", 0.0) > 0.05
            or self._history_float(row, "stage_seedvr2_seconds", 0.0) > 0.05
            or self._history_float(row, "stage_native_vsr_seconds", 0.0) > 0.05
        )
        # Correct legacy 1X rows where upscale_used=0 incorrectly meant
        # "did not enlarge" even though an AI stage actually ran.
        upscale_used = bool(inferred_upscale_used or self._history_bool(row, "upscale_used", False))

        seed_batch = int(round(self._history_float(row, "seed_frames_per_batch", 0.0)))
        seed_overlap = int(round(self._history_float(row, "seed_overlap", 0.0)))
        seed_batches = int(round(self._history_float(row, "seed_expected_meta_batches", 0.0)))
        if algorithm == "SeedVR2" and seed_batch <= 0:
            out_pixels = max(1, ai_w * ai_h)
            raw = int(math.floor(SEED_REF_PIXEL_FRAMES / float(out_pixels)))
            raw = max(5, min(SEED_REF_BATCH, raw))
            seed_batch = max((b for b in SEED_BATCHES if b <= raw), default=5)
            fps_for_overlap = ai_fps if ai_fps > 1 else 25.0
            seed_overlap = int(round(8.0 * fps_for_overlap / 25.0))
            seed_overlap = max(4, min(12, seed_overlap))
            seed_overlap = max(4, (seed_overlap // 4) * 4)
            if seed_batch < 29:
                seed_overlap = 4
            seed_batches = int(math.ceil(max(1, ai_frames) / max(1, seed_batch)))

        raw_estimated = self._history_float(row, "raw_estimated_before_recalibration_seconds", 0.0)
        calibrated_estimated = self._history_float(row, "estimated_before_run_seconds", 0.0)
        if raw_estimated <= 0:
            raw_estimated = calibrated_estimated
        timing_ratio = runtime / raw_estimated if raw_estimated > 0 else 0.0
        iterative_raw = str(row.get("iterative_restoration_used", "") or "").strip()
        iterative_known = bool(iterative_raw)
        iterative_used = self._history_bool(row, "iterative_restoration_used", False) if iterative_known else False
        iterative_plan_id = str(row.get("iterative_restoration_plan_id", "") or "").strip()
        iterative_target_factor = self._history_float(row, "iterative_restoration_target_factor", 0.0)
        iterative_ai_passes = int(round(self._history_float(row, "iterative_restoration_ai_passes", 0.0)))

        return {
            "runtime": runtime,
            "source_content_sha256": str(row.get("source_content_sha256", "") or ""),
            "configuration_sha256": str(row.get("configuration_sha256", "") or ""),
            "estimated_before": calibrated_estimated,
            "raw_estimated_before": raw_estimated,
            "timing_ratio": timing_ratio,
            "iterative_known": iterative_known,
            "iterative_used": iterative_used,
            "iterative_plan_id": iterative_plan_id,
            "iterative_target_factor": iterative_target_factor,
            "iterative_ai_passes": iterative_ai_passes,
            "algorithm": algorithm,
            "mode": mode,
            "scale": scale,
            "length": length,
            "source_w": sw,
            "source_h": sh,
            "source_fps": source_fps,
            "source_pixels": max(1.0, float(sw * sh)),
            "file_size": self._history_float(row, "file_size_bytes", 0.0),
            "reduce_enabled": reduce_enabled,
            "reduce_mode": reduce_mode if reduce_enabled else "Off",
            "reduce_value": reduce_value if reduce_enabled else 0.0,
            "ai_fps": ai_fps,
            "ai_frames": ai_frames,
            "ai_w": ai_w,
            "ai_h": ai_h,
            "ai_pixels": max(1.0, ai_pixels),
            "ai_pixel_rate": max(1.0, ai_pixel_rate),
            "workload": max(1.0, workload),
            "upscale_used": bool(upscale_used),
            "seed_batch": seed_batch,
            "seed_overlap": seed_overlap,
            "seed_batches": seed_batches,
            "rife_used": rife_used,
            "rife_multiplier": rife_multiplier,
            "rife_gpu_threads": rife_gpu_threads,
            "rife_input_fps": rife_input_fps,
            "rife_output_fps": rife_output_fps,
            "rife_input_frames": rife_input_frames,
            "rife_output_frames": rife_output_frames,
            "rife_generated_frames": rife_generated_frames,
            "rife_pixels": max(1.0, rife_pixels),
            "rife_generated_pixel_frames": max(0.0, rife_generated_pixel_frames),
            "final_encode_pixel_frames": max(1.0, final_encode_pixel_frames),
            "final_encoder": str(row.get("final_encoder", "") or "").strip() or "NVIDIA NVENC (fast)",
            "final_quality": str(row.get("final_quality", "") or "").strip() or "Medium",
            "final_quality_value": int(round(self._history_float(row, "final_quality_value", 24.0))),
            "final_encoder_threads": int(round(self._history_float(row, "final_encoder_threads", 0.0))),
            "expected_bitrate_mbps": self._history_float(row, "expected_bitrate_mbps", 0.0),
            "rife_pipeline_workload": max(0.0, rife_pipeline_workload),
            "source_decode_workload": source_decode_workload,
            "pre_ai_workload": pre_ai_workload,
            "enhancement_workload": enhancement_workload,
            "repair": self._history_bool(row, "repair_enabled", True),
            "stage_probe": self._history_float(row, "stage_probe_seconds", 0.0),
            "stage_repair": self._history_float(row, "stage_repair_seconds", 0.0),
            "stage_fps_reduce": self._history_float(row, "stage_fps_reduce_seconds", 0.0),
            "stage_denoise": self._history_float(row, "stage_denoise_seconds", 0.0),
            "stage_ai": self._history_float(row, "stage_ai_seconds", 0.0),
            "preseed_mode": str(row.get("preseed_mode", "") or ""),
            "pre_neural_downscale_factor": self._history_float(row, "pre_neural_downscale_factor", 1.0),
            "pre_neural_input_pixels": self._history_float(row, "pre_neural_input_pixels", float(sw*sh)),
            "preseed_factor": self._history_float(row, "preseed_factor", 0.0),
            "seedvr2_factor": self._history_float(row, "seedvr2_factor", 0.0),
            "stage_pre_neural_downscale": self._history_float(row, "stage_pre_neural_downscale_seconds", 0.0),
            "stage_native_vsr": self._history_float(row, "stage_native_vsr_seconds", 0.0),
            "stage_preseed_resize": self._history_float(row, "stage_preseed_resize_seconds", 0.0),
            "stage_seedvr2": self._history_float(row, "stage_seedvr2_seconds", 0.0),
            "stage_enhancement": self._history_float(row, "stage_enhancement_seconds", 0.0),
            "stage_rife": self._history_float(row, "stage_rife_seconds", 0.0),
            "stage_encode": self._history_float(row, "stage_encode_seconds", 0.0),
            "stage_other": self._history_float(row, "stage_other_seconds", 0.0),
            "seed_nvidia_launch_mode": seed_nvidia_launch_mode,
            "seed_disable_dynamic_vram": bool(seed_disable_dynamic_vram),
            "seed_disable_async_offload": bool(seed_disable_async_offload),
            "denoise": str(row.get("denoise_setting", "") or "").strip(),
            "color": str(row.get("color_setting", "") or "").strip(),
            "brightness": str(row.get("brightness_setting", "") or "").strip(),
            "white": str(row.get("white_setting", "") or "").strip(),
        }

    def _transformation_similarity(self, target: Dict[str, Any], hist: Dict[str, Any]) -> float:
        if hist["algorithm"] != target["algorithm"]:
            return 0.0

        def rel_close(a: float, b: float, tol: float = 0.002) -> bool:
            a = float(a); b = float(b)
            return abs(a - b) <= tol * max(1.0, abs(a), abs(b))

        preprocessing_exact = True
        for key in ("denoise", "color", "brightness", "white"):
            hv = str(hist.get(key, "") or "").strip()
            tv = str(target.get(key, "") or "").strip()
            if hv and tv and hv != tv:
                preprocessing_exact = False
                break

        mode_equivalent = (
            str(hist.get("mode", "")) == str(target.get("mode", ""))
        )

        exact = (
            mode_equivalent
            and int(hist.get("source_w", 0)) == int(target.get("source_w", 0))
            and int(hist.get("source_h", 0)) == int(target.get("source_h", 0))
            and rel_close(hist.get("scale", 1), target.get("scale", 1), 0.001)
            and int(hist.get("ai_w", 0)) == int(target.get("ai_w", 0))
            and int(hist.get("ai_h", 0)) == int(target.get("ai_h", 0))
            and bool(hist.get("upscale_used", True)) == bool(target.get("upscale_used", True))
            and bool(hist.get("rife_used")) == bool(target.get("rife_used"))
            and int(hist.get("rife_multiplier", 1)) == int(target.get("rife_multiplier", 1))
            and (
                not bool(target.get("rife_used"))
                or (
                    int(hist.get("rife_gpu_threads", 0)) > 0
                    and int(hist.get("rife_gpu_threads", 0)) == int(target.get("rife_gpu_threads", 0))
                )
            )
            and preprocessing_exact
            and str(hist.get("final_encoder", "")) == str(target.get("final_encoder", ""))
            and str(hist.get("final_quality", "")) == str(target.get("final_quality", ""))
            and (
                str(target.get("final_encoder", "")) != "libx265 CPU (best compression)"
                or int(hist.get("final_encoder_threads", 0)) == int(target.get("final_encoder_threads", 0))
            )
            and (
                target["algorithm"] != "SeedVR2"
                or (
                    int(hist.get("seed_batch", 0)) == int(target.get("seed_batch", 0))
                    and bool(str(hist.get("seed_nvidia_launch_mode", "") or "").strip())
                    and str(hist.get("seed_nvidia_launch_mode", "")) == str(target.get("seed_nvidia_launch_mode", ""))
                    and bool(hist.get("seed_disable_dynamic_vram", False)) == bool(target.get("seed_disable_dynamic_vram", False))
                    and bool(hist.get("seed_disable_async_offload", False)) == bool(target.get("seed_disable_async_offload", False))
                )
            )
        )
        if exact:
            return 100.0


        distance = 0.0
        distance += 0.52 * self._safe_log_ratio(target["ai_pixels"], hist["ai_pixels"])
        distance += 0.16 * self._safe_log_ratio(target["scale"], hist["scale"])
        distance += 0.10 * self._safe_log_ratio(target["source_pixels"], hist["source_pixels"])

        if str(hist.get("mode", "")) != str(target.get("mode", "")):
            distance += 0.18
        if bool(hist.get("upscale_used", True)) != bool(target.get("upscale_used", True)):
            distance += 0.45
        if bool(hist.get("rife_used")) != bool(target.get("rife_used")):
            distance += 0.22
        elif bool(target.get("rife_used")):
            distance += 0.06 * self._safe_log_ratio(
                max(1, target.get("rife_multiplier", 1)),
                max(1, hist.get("rife_multiplier", 1)),
            )
            hist_threads = int(hist.get("rife_gpu_threads", 0) or 0)
            target_threads = int(target.get("rife_gpu_threads", 0) or 0)
            if hist_threads <= 0:
                distance += 0.08
            else:
                distance += 0.08 * self._safe_log_ratio(
                    max(1, target_threads),
                    max(1, hist_threads),
                )

        if target["algorithm"] == "SeedVR2":
            distance += 0.12 * self._safe_log_ratio(
                max(1, target.get("seed_batch", 1)),
                max(1, hist.get("seed_batch", 1)),
            )
            hist_launch = str(hist.get("seed_nvidia_launch_mode", "") or "").strip()
            target_launch = str(target.get("seed_nvidia_launch_mode", "") or "").strip()
            if not hist_launch:
                distance += 0.10
            elif hist_launch != target_launch:
                distance += 0.16
            if bool(hist.get("seed_disable_dynamic_vram", False)) != bool(target.get("seed_disable_dynamic_vram", False)):
                distance += 0.12
            if bool(hist.get("seed_disable_async_offload", False)) != bool(target.get("seed_disable_async_offload", False)):
                distance += 0.12

        if str(hist.get("final_quality", "")) != str(target.get("final_quality", "")):
            distance += 0.05
        if str(target.get("final_encoder", "")) == "libx265 CPU (best compression)":
            hist_threads = max(1, int(hist.get("final_encoder_threads", 1) or 1))
            target_threads = max(1, int(target.get("final_encoder_threads", 1) or 1))
            distance += 0.10 * self._safe_log_ratio(target_threads, hist_threads)

        for key in ("denoise", "color", "brightness", "white"):
            hv = str(hist.get(key, "") or "").strip()
            tv = str(target.get(key, "") or "").strip()
            if hv and tv and hv != tv:
                distance += 0.025


        return max(1.0, min(99.0, 100.0 * math.exp(-1.4 * distance)))

    def _upscale_similarity(self, target: Dict[str, Any], hist: Dict[str, Any]) -> float:
        if hist["algorithm"] != target["algorithm"]:
            return 0.0

        def rel_close(a: float, b: float, tol: float = 0.002) -> bool:
            a = float(a)
            b = float(b)
            return abs(a - b) <= tol * max(1.0, abs(a), abs(b))

        spatial_exact = (
            int(hist.get("source_w", 0)) == int(target.get("source_w", 0))
            and int(hist.get("source_h", 0)) == int(target.get("source_h", 0))
            and int(hist.get("ai_w", 0)) == int(target.get("ai_w", 0))
            and int(hist.get("ai_h", 0)) == int(target.get("ai_h", 0))
            and rel_close(hist.get("scale", 1.0), target.get("scale", 1.0), 0.001)
        )

        hist_launch = str(hist.get("seed_nvidia_launch_mode", "") or "").strip()
        target_launch = str(target.get("seed_nvidia_launch_mode", "") or "").strip()
        launch_known_match = (
            bool(hist_launch)
            and bool(target_launch)
            and hist_launch == target_launch
        )
        launch_unknown = not hist_launch or not target_launch
        batch_exact = int(hist.get("seed_batch", 0) or 0) == int(target.get("seed_batch", 0) or 0)
        memory_flags_exact = (
            bool(hist.get("seed_disable_dynamic_vram", False)) == bool(target.get("seed_disable_dynamic_vram", False))
            and bool(hist.get("seed_disable_async_offload", False)) == bool(target.get("seed_disable_async_offload", False))
        )

        if spatial_exact and batch_exact and launch_known_match and memory_flags_exact:
            return 100.0

        if spatial_exact and batch_exact and launch_unknown and memory_flags_exact:
            return 96.0

        distance = 0.0
        distance += 0.58 * self._safe_log_ratio(
            max(1.0, target.get("ai_pixels", 1.0)),
            max(1.0, hist.get("ai_pixels", 1.0)),
        )
        distance += 0.20 * self._safe_log_ratio(
            max(1.0, target.get("scale", 1.0)),
            max(1.0, hist.get("scale", 1.0)),
        )
        distance += 0.12 * self._safe_log_ratio(
            max(1.0, target.get("source_pixels", 1.0)),
            max(1.0, hist.get("source_pixels", 1.0)),
        )

        if target["algorithm"] == "SeedVR2":
            distance += 0.08 * self._safe_log_ratio(
                max(1, target.get("seed_batch", 1)),
                max(1, hist.get("seed_batch", 1)),
            )
            hist_launch = str(hist.get("seed_nvidia_launch_mode", "") or "").strip()
            target_launch = str(target.get("seed_nvidia_launch_mode", "") or "").strip()
            if hist_launch and target_launch and hist_launch != target_launch:
                distance += 0.14
            elif not hist_launch or not target_launch:
                distance += 0.03
            if bool(hist.get("seed_disable_dynamic_vram", False)) != bool(target.get("seed_disable_dynamic_vram", False)):
                distance += 0.10
            if bool(hist.get("seed_disable_async_offload", False)) != bool(target.get("seed_disable_async_offload", False)):
                distance += 0.10

        return max(1.0, min(99.0, 100.0 * math.exp(-1.4 * distance)))

    def _ai_stage_similarity(self, target: Dict[str, Any], hist: Dict[str, Any]) -> float:
        return self._upscale_similarity(target, hist)

    def _rife_stage_similarity(self, target: Dict[str, Any], hist: Dict[str, Any]) -> float:
        if not target.get("rife_used") or not hist.get("rife_used"):
            return 0.0
        if int(target.get("rife_gpu_threads", 0)) != int(hist.get("rife_gpu_threads", 0)):
            thread_penalty = 0.16
        else:
            thread_penalty = 0.0
        distance = 0.0
        distance += 0.72 * self._safe_log_ratio(target.get("ai_pixels", 1), hist.get("ai_pixels", 1))
        distance += 0.10 * self._safe_log_ratio(target.get("source_pixels", 1), hist.get("source_pixels", 1))
        distance += thread_penalty
        return max(1.0, min(100.0, 100.0 * math.exp(-1.4 * distance)))

    def _generic_stage_similarity(self, target: Dict[str, Any], hist: Dict[str, Any], use_ai_pixels: bool) -> float:
        if hist["algorithm"] != target["algorithm"]:
            return 0.0
        if use_ai_pixels:
            distance = 0.78 * self._safe_log_ratio(target.get("ai_pixels", 1), hist.get("ai_pixels", 1))
        else:
            distance = 0.78 * self._safe_log_ratio(target.get("source_pixels", 1), hist.get("source_pixels", 1))
        return max(1.0, min(100.0, 100.0 * math.exp(-1.4 * distance)))

    def _predict_stage_seconds(
        self,
        target: Dict[str, Any],
        history: List[Dict[str, Any]],
        stage_key: str,
        workload_key: str,
        similarity_mode: str,
    ) -> Optional[float]:
        candidates: List[Tuple[float, float]] = []
        for hist in history:
            seconds = float(hist.get(stage_key, 0.0) or 0.0)
            if seconds <= 0:
                continue
            hist_work = float(hist.get(workload_key, 0.0) or 0.0)
            target_work = float(target.get(workload_key, 0.0) or 0.0)
            if hist_work <= 0 or target_work <= 0:
                continue
            if similarity_mode == "ai":
                similarity = self._ai_stage_similarity(target, hist)
            elif similarity_mode == "rife":
                similarity = self._rife_stage_similarity(target, hist)
            elif similarity_mode == "ai_pixels":
                similarity = self._generic_stage_similarity(target, hist, True)
            else:
                similarity = self._generic_stage_similarity(target, hist, False)
            if similarity <= 0:
                continue
            predicted = seconds * (target_work / hist_work)
            weight = max(1e-9, (similarity / 100.0) ** 8)
            candidates.append((max(0.0, predicted), weight))

        if not candidates:
            return None
        median = self._weighted_median(candidates)
        robust = [
            (value, weight)
            for value, weight in candidates
            if median <= 0 or (median / 3.0 <= value <= median * 3.0)
        ]
        if not robust:
            robust = candidates
        total_w = sum(weight for _value, weight in robust)
        if total_w <= 0:
            return sum(value for value, _weight in robust) / len(robust)
        return sum(value * weight for value, weight in robust) / total_w

    def _prediction_target_without_rife(self, target: Dict[str, Any]) -> Dict[str, Any]:
        base = copy.deepcopy(target)
        length = max(0.001, float(base.get("length", 0.001) or 0.001))
        ai_fps = max(1e-6, float(base.get("ai_fps", 0.0) or 0.0))
        ai_frames = max(1, int(base.get("ai_frames", 0) or round(length * ai_fps)))
        out_w = max(1, int(base.get("out_w", 0) or base.get("ai_w", 1) or 1))
        out_h = max(1, int(base.get("out_h", 0) or base.get("ai_h", 1) or 1))
        base["rife_used"] = False
        base["rife_multiplier"] = 1
        base["rife_gpu_threads"] = 0
        base["rife_input_fps"] = float(self._round_fps(ai_fps))
        base["rife_output_fps"] = float(self._round_fps(ai_fps))
        base["rife_input_frames"] = int(ai_frames)
        base["rife_output_frames"] = int(ai_frames)
        base["rife_generated_frames"] = 0
        base["rife_generated_pixel_frames"] = 0.0
        base["rife_pipeline_workload"] = 0.0
        base["out_fps"] = float(self._round_fps(ai_fps))
        base["final_encode_pixel_frames"] = max(
            1.0,
            float(out_w) * float(out_h) * float(ai_frames),
        )
        return base

    def _stage_aware_estimate(self, target: Dict[str, Any], history: List[Dict[str, Any]]) -> Optional[float]:
        stage_rows = [h for h in history if any(float(h.get(k, 0.0) or 0.0) > 0 for k in (
            "stage_ai", "stage_rife", "stage_encode", "stage_denoise", "stage_enhancement"
        ))]
        if not stage_rows:
            return None

        total = 0.0
        required_missing = False

        probe = self._predict_stage_seconds(target, stage_rows, "stage_probe", "source_decode_workload", "source")
        if probe is not None:
            total += probe

        if target.get("repair"):
            repair = self._predict_stage_seconds(target, stage_rows, "stage_repair", "source_decode_workload", "source")
            if repair is not None:
                total += repair

        if target.get("reduce_enabled"):
            fps_reduce = self._predict_stage_seconds(target, stage_rows, "stage_fps_reduce", "source_decode_workload", "source")
            if fps_reduce is not None:
                total += fps_reduce

        if str(target.get("denoise", "")) == "Auto":
            denoise = self._predict_stage_seconds(target, stage_rows, "stage_denoise", "pre_ai_workload", "source")
            if denoise is not None:
                total += denoise

        if target.get("upscale_used", True):
            ai = self._predict_stage_seconds(target, stage_rows, "stage_ai", "workload", "ai")
            if ai is None:
                required_missing = True
            else:
                total += ai

        if any(str(target.get(k, "")) == "Auto" for k in ("color", "brightness", "white")):
            enhancement = self._predict_stage_seconds(target, stage_rows, "stage_enhancement", "enhancement_workload", "ai_pixels")
            if enhancement is not None:
                total += enhancement

        if target.get("rife_used"):
            base_target = self._prediction_target_without_rife(target)
            base_encode = self._predict_stage_seconds(
                base_target,
                stage_rows,
                "stage_encode",
                "final_encode_pixel_frames",
                "ai_pixels",
            )
            rife_pipeline = self._predict_stage_seconds(
                target,
                stage_rows,
                "stage_rife",
                "rife_pipeline_workload",
                "rife",
            )
            if rife_pipeline is None:
                required_missing = True
            else:
                if base_encode is not None:
                    total += max(float(rife_pipeline), float(base_encode) + 1.0)
                else:
                    total += float(rife_pipeline)
        else:
            encode = self._predict_stage_seconds(target, stage_rows, "stage_encode", "final_encode_pixel_frames", "ai_pixels")
            if encode is not None:
                total += encode

        other_values = [float(h.get("stage_other", 0.0) or 0.0) for h in stage_rows if float(h.get("stage_other", 0.0) or 0.0) > 0]
        if other_values:
            total += self._median_value(other_values) or 0.0

        if required_missing or total <= 0:
            return None
        return total

    @staticmethod
    def _weighted_median(values: List[Tuple[float, float]]) -> float:
        if not values:
            return 0.0
        ordered = sorted((float(v), max(0.0, float(w))) for v, w in values)
        total = sum(w for _v, w in ordered)
        if total <= 0:
            return ordered[len(ordered) // 2][0]
        cutoff = total * 0.5
        acc = 0.0
        for value, weight in ordered:
            acc += weight
            if acc >= cutoff:
                return value
        return ordered[-1][0]

    def _estimate_target_from_parsed_history(
        self,
        target: Dict[str, Any],
        parsed_history: List[Dict[str, Any]],
    ) -> Tuple[Optional[float], float]:
        same_rife_state = [
            hist
            for hist in parsed_history
            if bool(hist.get("rife_used")) == bool(target.get("rife_used"))
            and bool(hist.get("upscale_used", True)) == bool(target.get("upscale_used", True))
        ]
        history_for_runtime = same_rife_state if same_rife_state else parsed_history
        candidates: List[Dict[str, float]] = []

        for hist in history_for_runtime:
            if hist.get("algorithm") != target.get("algorithm"):
                continue
            pipeline_similarity = self._transformation_similarity(target, hist)
            upscale_similarity = self._upscale_similarity(target, hist)
            if pipeline_similarity <= 0 or upscale_similarity <= 0:
                continue
            predicted = float(hist["runtime"]) * (
                float(target["workload"]) / max(1.0, float(hist["workload"]))
            )
            candidates.append({
                "similarity": float(pipeline_similarity),
                "upscale_similarity": float(upscale_similarity),
                "predicted": max(1.0, float(predicted)),
            })

        if not candidates:
            return None, 0.0

        candidates.sort(key=lambda x: x["similarity"], reverse=True)
        pipeline_best_similarity = float(candidates[0]["similarity"])
        if bool(target.get("rife_used")) and not bool(target.get("upscale_used", True)):
            best_similarity = max(float(c["similarity"]) for c in candidates)
        else:
            best_similarity = max(float(c["upscale_similarity"]) for c in candidates)
        floor = max(25.0, pipeline_best_similarity - 35.0)
        selected = [c for c in candidates if c["similarity"] >= floor][:24]
        if not selected:
            selected = candidates[:1]

        weighted_values: List[Tuple[float, float]] = []
        for candidate in selected:
            weight = max(1e-9, (float(candidate["similarity"]) / 100.0) ** 8)
            weighted_values.append((float(candidate["predicted"]), weight))

        median = self._weighted_median(weighted_values)
        robust = [
            (value, weight)
            for value, weight in weighted_values
            if median <= 0 or (median / 3.0 <= value <= median * 3.0)
        ]
        if not robust:
            robust = weighted_values

        total_w = sum(weight for _value, weight in robust)
        estimate = (
            sum(value * weight for value, weight in robust) / total_w
            if total_w > 0
            else sum(value for value, _weight in robust) / len(robust)
        )

        stage_estimate = self._stage_aware_estimate(target, parsed_history)
        if stage_estimate is not None:
            estimate = float(stage_estimate)

        return max(1.0, float(estimate)), float(best_similarity)

    def _estimate_neural_preseed_seconds(self, target: Dict[str, Any],
                                       history: List[Dict[str, Any]]) -> Optional[float]:
        """Estimate VSR 4X and SeedVR2 stages independently.

        Unlike V242, the VSR component is NEVER multiplied by requested
        pre-SeedVR2 factor: BasicVSR++ runs native 4X for both 2X and 4X.
        The subsequent bicubic operation and SeedVR2 have separate costs.
        Historic V242 rows do not identify the neural model/stages, so they
        are not treated as reliable neural performance benchmarks.
        """
        mode = str(target.get("preseed_mode", ""))
        neural = [h for h in history if h.get("preseed_mode") == mode
                  and float(h.get("stage_native_vsr", 0) or 0) > 0]
        if not neural:
            return None
        src_work = (max(1.0, float(target.get("pre_neural_input_pixels", target.get("source_pixels", 1))))
                    * max(1.0, float(target.get("ai_frames", 1))))
        neural_values = []
        for h in neural:
            h_work = max(1.0, float(h.get("pre_neural_input_pixels", h.get("source_pixels", 1)))
                         * max(1.0, float(h.get("ai_frames", 1))))
            # Native 4X model identical regardless of final factor.
            rate = float(h["stage_native_vsr"]) * src_work / h_work
            neural_values.append((rate, 1.0 / (1.0 + abs(math.log(src_work / h_work)))))
        predicted_native = self._weighted_median(neural_values)
        needs_resize = abs(float(target.get("preseed_factor", 4.0)) - 4.0) > 0.0001
        predicted_resize = 0.0
        if needs_resize:
            resize_samples = [h for h in neural if float(h.get("stage_preseed_resize", 0) or 0) > 0]
            if resize_samples:
                predicted_resize = self._weighted_median([
                    (float(h["stage_preseed_resize"]) *
                     src_work / max(1.0, float(h.get("pre_neural_input_pixels", h.get("source_pixels", 1))) * float(h.get("ai_frames", 1))), 1.0)
                    for h in resize_samples
                ])
            else:
                # Without a measured bicubic sample, leave its ETA unquantified
                # rather than invent a percentage of the neural workload.
                predicted_resize = 0.0
        # SeedVR2 cost depends strongly on actual output pixel frames.
        seed_rows = [h for h in history if float(h.get("stage_seedvr2", 0) or 0) > 0]
        if not seed_rows:
            return None
        seed_values = []
        target_work = max(1.0, float(target.get("workload", 1)))
        for h in seed_rows:
            old_work = max(1.0, float(h.get("workload", 1)))
            scaled = float(h["stage_seedvr2"]) * target_work / old_work
            weight = 1 / (1 + abs(math.log(target_work / old_work)))
            seed_values.append((scaled, weight))
        predicted_seed = self._weighted_median(seed_values)
        # Other post-/pre-processing stages estimated from their own history.
        rows = [h for h in history if float(h.get("stage_encode", 0) or 0) > 0]
        encode = self._predict_stage_seconds(target, rows, "stage_encode", "final_encode_pixel_frames", "ai_pixels") if rows else None
        reduction_samples = [h for h in neural if float(h.get("stage_pre_neural_downscale", 0) or 0) > 0]
        predicted_pre_neural = (self._weighted_median([
            (float(h["stage_pre_neural_downscale"]) *
             float(target.get("source_pixels", 1)) * float(target.get("ai_frames", 1)) /
             max(1.0, float(h.get("source_pixels", 1)) * float(h.get("ai_frames", 1))), 1.0)
            for h in reduction_samples]) if reduction_samples and
            float(target.get("pre_neural_downscale_factor", 1.0)) < 0.999999 else 0.0)
        processing_misc = max(2.0, float(target.get("length", 1)) * 0.04)
        return max(1.0, predicted_pre_neural + predicted_native + predicted_resize + predicted_seed + max(0.0, encode or 0.0) + processing_misc)

    @staticmethod
    def _v248_sampled_content_sha256(path: Path, *, sample_bytes: int = 1048576) -> str:
        """Anonymous deterministic sampled SHA256; no source basename or path in CSV."""
        try:
            size = int(path.stat().st_size)
            if size < 0:
                return ""
            h = hashlib.sha256()
            h.update(b"Upscaler-source-sampled-sha256-v1\0")
            h.update(str(size).encode("ascii"))
            h.update(b"\0")
            with path.open("rb") as handle:
                offsets = sorted({0, max(0, size // 2 - sample_bytes // 2), max(0, size - sample_bytes)})
                for off in offsets:
                    handle.seek(off)
                    data = handle.read(sample_bytes)
                    h.update(str(off).encode("ascii") + b":" + str(len(data)).encode("ascii") + b"\0")
                    h.update(data)
            return h.hexdigest()
        except (OSError, ValueError):
            return ""

    def _v248_source_fingerprint(self, path: Path) -> str:
        try:
            st = path.stat()
            key = (str(path), int(st.st_size), int(st.st_mtime_ns))
            cached = self._content_fingerprint_cache.get(key)
            if cached is not None:
                return cached
            digest = self._v248_sampled_content_sha256(path)
            if len(self._content_fingerprint_cache) > 120:
                self._content_fingerprint_cache.clear()
            self._content_fingerprint_cache[key] = digest
            return digest
        except OSError:
            return ""

    def _v248_checkpoint_digest(self, setting_name: str, setting_var: tk.Variable) -> str:
        """Hash a model/config file, not its path or filename; only digest enters CSV."""
        try:
            path = Path(str(self._job_setting(setting_name, setting_var)).strip().strip('"'))
            st = path.stat()
            key = (str(path), int(st.st_size), int(st.st_mtime_ns))
            cached = self._checkpoint_fingerprint_cache.get(key)
            if cached is not None:
                return cached
            # Hash the model's distributed file bytes sampled at three positions.
            digest = self._v248_sampled_content_sha256(path, sample_bytes=65536)
            if len(self._checkpoint_fingerprint_cache) > 32:
                self._checkpoint_fingerprint_cache.clear()
            self._checkpoint_fingerprint_cache[key] = digest
            return digest
        except (OSError, ValueError):
            # Unknown checkpoint bytes must NOT be advertised as a verified match.
            return ""

    def _v248_configuration_signature(self, target: Dict[str, Any]) -> Tuple[str, str, str]:
        """Build a stable full-pipeline signature, independent of source filenames."""
        def norm(value: Any) -> Any:
            if isinstance(value, float):
                return round(value, 6)
            if isinstance(value, (str, int, bool)) or value is None:
                return value
            return str(value)

        values = {
            "schema": "V257-2stage-restoration-v1",
            # Source properties belong to config only as geometry/workload, not identity.
            "features": {k: norm(target.get(k)) for k in (
                "algorithm", "mode", "scale", "length", "source_w", "source_h",
                "source_fps", "ai_fps", "ai_frames", "ai_w", "ai_h", "out_w", "out_h",
                "out_fps", "reduce_enabled", "reduce_mode", "reduce_value",
                "upscale_used", "preseed_mode", "pre_neural_downscale_factor",
                "preseed_factor", "seedvr2_factor", "seed_batch", "seed_overlap",
                "rife_used", "rife_multiplier", "rife_gpu_threads", "rife_input_fps",
                "rife_output_fps", "final_encoder", "final_quality", "final_quality_value",
                "final_encoder_threads", "repair", "denoise", "color", "brightness",
                "white", "seed_nvidia_launch_mode",
                "seed_disable_dynamic_vram", "seed_disable_async_offload",
            )},
        }
        options = (
            ("upscale_enable", self.upscale_enable),
            ("downscale_enable", self.downscale_enable),
            ("downscale_preset", self.downscale_preset),
            ("downscale_custom", self.downscale_custom),
            ("enhancement_enable", self.enhancement_enable),
            ("deinterlace_auto", self.deinterlace_auto),
            ("sharpen", self.sharpen), ("deband", self.deband),
            ("seed_parameter_mode", self.seed_parameter_mode),
            ("seed_batch_max", self.seed_batch_max),
            ("seed_temporal_overlap", self.seed_temporal_overlap),
            ("seed_vae_tile", self.seed_vae_tile),
            ("seed_vae_spatial_overlap", self.seed_vae_spatial_overlap),
            ("rife_mode", self.rife_mode),
            ("rife_target_fps", self.rife_target_fps),
            ("rife_multiplier", self.rife_multiplier),
            ("rife_gpu_thread", self.rife_gpu_thread),
            ("native_sr_max_seq_len", self.native_sr_max_seq_len),
            ("native_sr_chunk_frames", self.native_sr_chunk_frames),
            ("basicvsr_persistent_worker", self.basicvsr_persistent_worker),
            ("basicvsr_tile_profile", self.basicvsr_tile_profile),
            ("native_sr_model", self.native_sr_model),
            ("scaling_enable", self.scaling_enable),
            ("scaling1_enabled", self.scaling1_enabled),
            ("scaling1_method", self.scaling1_method),
            ("scaling1_factor", self.scaling1_factor),
            ("scaling1_target", self.scaling1_target),
            ("scaling2_enabled", self.scaling2_enabled),
            ("scaling2_method", self.scaling2_method),
            ("scaling2_factor", self.scaling2_factor),
            ("scaling2_target", self.scaling2_target),
            ("scaling3_enabled", self.scaling3_enabled),
            ("scaling3_method", self.scaling3_method),
            ("scaling3_factor", self.scaling3_factor),
            ("scaling3_target", self.scaling3_target),
            ("scaling4_target", self.scaling4_target),
            ("force_exact_resolution", self.force_exact_resolution),
        )
        values["options"] = {
            key: norm(self._job_setting(key, var)) for key, var in options
        }
        native_model = ""
        seed_model = ""
        if target.get("algorithm") == "SeedVR2":
            seed_model = self._v248_checkpoint_digest("workflow_json", self.workflow_json)
            values["workflow_digest"] = seed_model or "unknown"
            if bool(self._job_setting("scaling_enable", self.scaling_enable)) and any(
                    str(self._job_setting(f"scaling{i}_method", getattr(self, f"scaling{i}_method"))).startswith(("BasicVSR++", "RealBasicVSR"))
                    for i in (1, 2, 3, 4)):
                native_model = self._v248_checkpoint_digest("native_sr_checkpoint", self.native_sr_checkpoint)
                values["native_checkpoint_digest"] = native_model or "unknown"
                values["native_config_digest"] = (self._v248_checkpoint_digest("native_sr_config", self.native_sr_config) or "unknown")
        # Include identities of workflow-selected model weights as well as the workflow.
        # Hashes are anonymous: paths and source/video filenames are not saved in CSV.
        if target.get("algorithm") == "SeedVR2":
            model_weights = self._v248_seed_workflow_weights()
            if model_weights:
                values["workflow_weight_digests"] = model_weights
                seed_model = hashlib.sha256(
                    json.dumps(model_weights, sort_keys=True).encode("utf-8")
                ).hexdigest()
            elif not seed_model:
                values["workflow_weight_digests"] = "unavailable"
        serialized = json.dumps(values, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest(), seed_model, native_model

    def _v248_seed_workflow_weights(self) -> Dict[str, str]:
        """Identify model files selected by API workflow without exporting model paths.

        When a weight file can be resolved locally, digest sampled file bytes.
        When not resolvable, use its anonymous declared name digest with an
        explicit unresolved marker. No movie basename or path is stored.
        """
        try:
            workflow_path = Path(str(self._job_setting("workflow_json", self.workflow_json)).strip())
            workflow = json.loads(workflow_path.read_text(encoding="utf-8-sig"))
            if isinstance(workflow, dict) and isinstance(workflow.get("prompt"), dict):
                workflow = workflow["prompt"]
        except (OSError, ValueError, TypeError):
            return {}
        names = set()
        def collect(o: Any) -> None:
            if isinstance(o, dict):
                for v in o.values():
                    collect(v)
            elif isinstance(o, list):
                for v in o:
                    collect(v)
            elif isinstance(o, str) and re.search(r"\.(?:safetensors|ckpt|pth|pt)$", o, re.I):
                names.add(o)
        collect(workflow)
        if not names:
            return {}
        root = Path(str(self._job_setting("comfy_root", self.comfy_root)).strip())
        model_root = root / "ComfyUI" / "models"
        folders = (model_root, model_root / "diffusion_models", model_root / "unet",
                   model_root / "vae", model_root / "checkpoints", model_root / "text_encoders")
        result = {}
        for name in sorted(names):
            relative = Path(name.replace("\\", "/"))
            candidates = [relative] + [folder / relative for folder in folders]
            selected = next((c for c in candidates if c.is_file()), None)
            if selected is None and model_root.is_dir():
                # Lookup only explicit weight filenames; never scan video directories.
                try:
                    selected = next(model_root.rglob(relative.name), None)
                except OSError:
                    selected = None
            identifier = hashlib.sha256(name.encode("utf-8")).hexdigest()
            if selected is not None and selected.is_file():
                try:
                    st = selected.stat()
                    cachekey = (str(selected), int(st.st_size), int(st.st_mtime_ns))
                    digest = self._checkpoint_fingerprint_cache.get(cachekey)
                    if digest is None:
                        digest = self._v248_sampled_content_sha256(selected, sample_bytes=65536)
                        self._checkpoint_fingerprint_cache[cachekey] = digest
                    result[identifier] = "weight:" + digest
                except OSError:
                    result[identifier] = "unresolved"
            else:
                result[identifier] = "unresolved"
        return result

    @staticmethod
    def _v248_close_number(a: Any, b: Any, *, relative: float = 0.0005, absolute: float = 0.0005) -> bool:
        try:
            a, b = float(a), float(b)
            return abs(a - b) <= max(absolute, relative * max(abs(a), abs(b)))
        except (ValueError, TypeError):
            return False

    def _v248_legacy_metadata_compatible(self, target: Dict[str, Any], row: Dict[str, str]) -> bool:
        """Conservative fallback when historical source/config digests did not exist.

        Never claim the file bytes or checkpoint are verified from metadata alone.
        """
        def val(name: str) -> str:
            return str(row.get(name, "") or "").strip()
        def number(key: str, historic_key: str, **kw: Any) -> bool:
            return bool(val(historic_key)) and self._v248_close_number(target.get(key), val(historic_key), **kw)
        def same(key: str, historic_key: str) -> bool:
            return bool(val(historic_key)) and str(target.get(key)) == val(historic_key)
        def flag(key: str, historic_key: str) -> bool:
            return bool(val(historic_key)) and bool(target.get(key)) == self._history_bool(row, historic_key)

        # Metadata ties an old record to a probable source, but cannot prove content identity.
        for tkey, hkey in (
            ("file_size", "file_size_bytes"),
            ("source_w", "source_width"), ("source_h", "source_height"),
            ("source_fps", "source_fps"), ("length", "movie_length_seconds"),
            ("scale", "scale_factor"), ("ai_fps", "ai_input_fps"),
            ("ai_frames", "ai_input_frames"),
            ("seed_batch", "seed_frames_per_batch"), ("seed_overlap", "seed_overlap"),
            ("rife_output_fps", "rife_output_fps"),
            ("rife_multiplier", "rife_multiplier"),
            ("pre_neural_downscale_factor", "pre_neural_downscale_factor"),
            ("preseed_factor", "preseed_factor"),
            ("seedvr2_factor", "seedvr2_factor"),
        ):
            if not number(tkey, hkey, absolute=0.02 if tkey == "length" else 0.001):
                return False
        for tkey, hkey in (
            ("algorithm", "algorithm"), ("mode", "algorithm_mode"),
            ("preseed_mode", "preseed_mode"),
            ("final_encoder", "final_encoder"), ("final_quality", "final_quality"),
            ("seed_nvidia_launch_mode", "seed_nvidia_launch_mode"),
            ("denoise", "denoise_setting"), ("color", "color_setting"),
            ("brightness", "brightness_setting"), ("white", "white_setting"),
        ):
            if not same(tkey, hkey):
                return False
        for tkey, hkey in (
            ("rife_used", "rife_used"), ("reduce_enabled", "fps_reduce_enabled"),
            ("repair", "repair_enabled"),
            ("seed_disable_dynamic_vram", "seed_disable_dynamic_vram"),
            ("seed_disable_async_offload", "seed_disable_async_offload"),
        ):
            if not flag(tkey, hkey):
                return False
        if not number("final_quality_value", "final_quality_value"):
            return False
        if not number("final_encoder_threads", "final_encoder_threads"):
            return False
        return True

    def _v248_historical_exact_estimate(self, info: VideoInfo) -> Optional[Tuple[float, int, str, str]]:
        """Return (seconds, config similarity, matching strategy, evidence label)."""
        target = self._duration_estimation_features(info)
        source_hash = self._v248_source_fingerprint(info.path)
        config_hash, _, _ = self._v248_configuration_signature(target)
        new_exact: List[Dict[str, str]] = []
        legacy: List[Dict[str, str]] = []
        for row in self._load_duration_history():
            if row.get("algorithm") != target.get("algorithm"):
                continue
            elapsed = self._history_float(row, "processing_duration_seconds", 0.0)
            if elapsed <= 0:
                continue
            old_src = str(row.get("source_content_sha256", "") or "")
            old_config = str(row.get("configuration_sha256", "") or "")
            if old_src and old_config:
                if source_hash and old_src == source_hash and old_config == config_hash:
                    new_exact.append(row)
            elif (not old_src and not old_config and
                  self._v248_legacy_metadata_compatible(target, row)):
                legacy.append(row)
        if new_exact:
            newest = new_exact[-1]
            # Exact same source bytes (sample hash), full config and same model IDs.
            return (self._history_float(newest, "processing_duration_seconds"),
                    100, "exact_history", "High · source/config hash")
        if legacy:
            newest = legacy[-1]
            # Explicitly disclose the older format lacks source/model fingerprints.
            return (self._history_float(newest, "processing_duration_seconds"),
                    100, "legacy_metadata", "Moderate · legacy match")
        return None

    def _estimate_processing_seconds(self, info: VideoInfo) -> Tuple[Optional[float], int]:
        if info.width <= 0 or info.height <= 0 or info.duration <= 0:
            return None, 0

        target = self._duration_estimation_features(info)
        parsed_history: List[Dict[str, Any]] = []

        for row in self._load_duration_history():
            hist = self._history_estimation_features(row)
            if hist is None or hist["algorithm"] != target["algorithm"]:
                continue
            if str(hist.get("final_encoder", "")) != str(target.get("final_encoder", "")):
                continue
            parsed_history.append(hist)

        if not parsed_history:
            return None, 0

        if target.get("algorithm") == "SeedVR2" and target.get("preseed_mode") != "Only Bicubic":
            neural_time = self._estimate_neural_preseed_seconds(target, parsed_history)
            if neural_time is None:
                return None, 0
            matches = sum(1 for h in parsed_history if h.get("preseed_mode") == target["preseed_mode"]
                          and h.get("stage_native_vsr", 0) > 0)
            return max(1.0, neural_time), min(90, 45 + 10 * matches)

        if target.get("algorithm") == "SeedVR2":
            parsed_history = [h for h in parsed_history if h.get("preseed_mode") in ("", "Only Bicubic")]
            if not parsed_history:
                return None, 0

        estimate, best_similarity = self._estimate_target_from_parsed_history(
            target,
            parsed_history,
        )
        if estimate is None:
            return None, 0

        if target.get("rife_used"):
            no_rife_target = self._prediction_target_without_rife(target)
            no_rife_estimate, _base_similarity = self._estimate_target_from_parsed_history(
                no_rife_target,
                parsed_history,
            )
            if no_rife_estimate is not None:
                estimate = max(
                    float(estimate),
                    float(no_rife_estimate) + 1.0,
                )

        estimate = max(1.0, min(float(estimate), 365.0 * 24.0 * 3600.0))
        return estimate, int(round(best_similarity))

    def _timing_recalibration(self, info: VideoInfo) -> Tuple[float, int, int]:
        if info.width <= 0 or info.height <= 0 or info.duration <= 0:
            return 1.0, 0, 0
        target = self._duration_estimation_features(info)
        parsed: List[Dict[str, Any]] = []
        for row in self._load_duration_history():
            hist = self._history_estimation_features(row)
            if hist is None or hist.get("algorithm") != target.get("algorithm"):
                continue
            ratio = float(hist.get("timing_ratio", 0.0) or 0.0)
            if ratio <= 0.03 or ratio >= 20.0:
                continue
            parsed.append(hist)
        if not parsed:
            return 1.0, 0, 0

        if target.get("algorithm") == "SeedVR2" and target.get("preseed_mode") != "Only Bicubic":
            parsed = [h for h in parsed if h.get("preseed_mode") == target["preseed_mode"]]
            if not parsed:
                return 1.0, 0, 0
        candidates: List[Tuple[float, float, float]] = []
        total_rows = len(parsed)
        for idx, hist in enumerate(parsed):
            similarity = float(self._transformation_similarity(target, hist))
            if similarity < 30.0:
                continue
            ratio = max(0.08, min(8.0, float(hist.get("timing_ratio", 1.0) or 1.0)))
            age = max(0, total_rows - 1 - idx)
            recency = 0.93 ** min(age, 60)
            weight = max(1e-8, (similarity / 100.0) ** 6) * recency
            if weight <= 1e-7:
                continue
            candidates.append((ratio, weight, similarity))

        if not candidates:
            return 1.0, 0, 0
        candidates.sort(key=lambda item: item[1], reverse=True)
        candidates = candidates[:16]
        weighted = [(ratio, weight) for ratio, weight, _sim in candidates]
        median_ratio = self._weighted_median(weighted)
        robust = [
            (ratio, weight, sim)
            for ratio, weight, sim in candidates
            if median_ratio <= 0 or median_ratio / 2.5 <= ratio <= median_ratio * 2.5
        ]
        if not robust:
            robust = candidates
        total_weight = sum(weight for _ratio, weight, _sim in robust)
        mean_ratio = (
            sum(ratio * weight for ratio, weight, _sim in robust) / total_weight
            if total_weight > 0
            else median_ratio
        )
        raw_factor = max(0.10, min(6.0, 0.70 * median_ratio + 0.30 * mean_ratio))
        best_similarity = max(float(sim) for _ratio, _weight, sim in robust)
        sample_count = len(robust)
        if best_similarity >= 88.0:
            trust = 1.0
        elif best_similarity >= 75.0:
            trust = min(1.0, 0.72 + 0.08 * sample_count)
        elif best_similarity >= 60.0:
            trust = min(0.90, 0.52 + 0.07 * sample_count)
        else:
            trust = min(0.70, 0.35 + 0.05 * sample_count)
        factor = max(0.10, min(6.0, 1.0 + trust * (raw_factor - 1.0)))
        confidence = int(round(max(0.0, min(100.0, best_similarity * min(1.0, 0.55 + 0.09 * sample_count)))))
        return factor, sample_count, confidence

    @staticmethod
    def _fmt_prediction_duration(sec: float) -> str:
        try:
            total = max(0, int(round(float(sec))))
        except Exception:
            return "--"
        days, rem = divmod(total, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        parts: List[str] = []
        if days:
            parts.append(f"{days}d")
        if hours or days:
            parts.append(f"{hours}h")
        if minutes or hours or days:
            parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return "".join(parts)




    def _update_total_queue_estimate(self) -> None:
        if not hasattr(self, "total_queue_estimate_text"):
            return

        total_files = len(self.jobs)
        if total_files == 0:
            self.total_queue_estimate_text.set("Total queue estimated time: --")
            return

        mode_text = ""
        known = [
            float(job.estimated_seconds)
            for job in self.jobs
            if job.estimated_seconds is not None and float(job.estimated_seconds) >= 0
        ]
        unknown = total_files - len(known)

        if not known:
            self.total_queue_estimate_text.set(
                f"Total queue estimated time: Learning... ({total_files} file{'s' if total_files != 1 else ''})"
                + mode_text
            )
            return

        total_seconds = sum(known)
        total_text = self._fmt_prediction_duration(total_seconds)

        if unknown:
            self.total_queue_estimate_text.set(
                f"Total queue estimated time: {total_text} + {unknown} learning "
                f"({len(known)}/{total_files} files estimated)" + mode_text
            )
        else:
            self.total_queue_estimate_text.set(
                f"Total queue estimated time: {total_text} ({total_files} file{'s' if total_files != 1 else ''})"
                + mode_text
            )

    def _update_job_duration_estimate(self, job: Job, force: bool = False) -> None:


        # Freeze pre-run estimates for Running/Done jobs, including force refreshes.
        if job.status != "Queued":
            return
        if not force and job.status != "Queued":
            return

        target_now = self._job_settings_call(job, self._duration_estimation_features, job.info)
        job.history_source_sha256 = self._v248_source_fingerprint(job.info.path)
        (job.history_configuration_sha256, job.history_seed_model_id,
         job.history_native_model_id) = self._job_settings_call(
            job, self._v248_configuration_signature, target_now
        )
        direct_match = self._job_settings_call(job, self._v248_historical_exact_estimate, job.info)
        if direct_match is not None:
            estimate, similarity, job.prediction_basis, job.prediction_evidence = direct_match
            job.raw_estimated_seconds = float(estimate)
            job.estimated_seconds = float(estimate)
            job.estimate_similarity = int(similarity)
            job.estimate_similarity_text = f"{int(similarity)}%"
            job.estimate_text = self._fmt_prediction_duration(estimate)
            job.timing_recalibration_factor = 1.0
            job.timing_recalibration_samples = 0
            job.timing_recalibration_confidence = 0
            job.estimate_samples = 1
            return
        job.prediction_basis = "modeled"
        job.prediction_evidence = "Low · modeled"
        estimate, similarity = self._job_settings_call(job, self._estimate_processing_seconds, job.info)
        job.raw_estimated_seconds = float(estimate) if estimate is not None else None
        recalibration_factor = 1.0
        recalibration_samples = 0
        recalibration_confidence = 0
        if estimate is not None:
            try:
                recalibration_factor, recalibration_samples, recalibration_confidence = self._job_settings_call(
                    job, self._timing_recalibration, job.info
                )
                estimate = max(1.0, float(estimate) * float(recalibration_factor))
            except Exception:
                recalibration_factor, recalibration_samples, recalibration_confidence = 1.0, 0, 0
        job.timing_recalibration_factor = float(recalibration_factor)
        job.timing_recalibration_samples = int(recalibration_samples)
        job.timing_recalibration_confidence = int(recalibration_confidence)
        job.estimated_seconds = estimate
        if estimate is not None and int(similarity) >= 90:
            job.prediction_evidence = "Moderate · modeled"
        job.estimate_samples = int(recalibration_samples)
        job.estimate_similarity = int(similarity)
        if estimate is None:
            job.estimate_text = "Learning..."
            job.estimate_similarity_text = "--"
        else:
            job.estimate_text = self._fmt_prediction_duration(estimate)
            job.estimate_similarity_text = f"{int(similarity)}%"

    def _recalibrate_queued_duration_estimates_after_actual(self, completed_job: Job, actual_seconds: float) -> None:
        changed = 0
        old_prediction = float(completed_job.estimated_seconds or 0.0)
        ratio = actual_seconds / old_prediction if old_prediction > 0 else 0.0
        for pending in self.jobs:
            if pending is completed_job or pending.status != "Queued":
                continue
            before = float(pending.estimated_seconds or 0.0)
            self._update_job_duration_estimate(pending, force=True)
            after = float(pending.estimated_seconds or 0.0)
            if before <= 0 or abs(after - before) >= max(10.0, before * 0.02):
                changed += 1
            self._post("job", pending)
        self._update_total_queue_estimate()
        self._post(
            "log",
            f"V193 ETA RECALIBRATION: completed={completed_job.info.path.name}; "
            f"actual={self._fmt_prediction_duration(actual_seconds)}; "
            f"last_prediction={self._fmt_prediction_duration(old_prediction) if old_prediction > 0 else '--'}; "
            f"actual/predicted={ratio:.3f} if available; recalculated queued jobs={changed}."
        )

    def _refresh_duration_estimates(self) -> None:
        for job in self.jobs:
            self._update_job_duration_estimate(job)
            self._update_job_row(job)
        self._update_total_queue_estimate()

    @staticmethod



    @staticmethod


























    @staticmethod








    def _update_stop_button_state(self) -> None:
        try:
            active = bool(
                (self.worker and self.worker.is_alive())
            )
            self.stop_btn.configure(state="normal" if active else "disabled")
        except Exception:
            pass




    @staticmethod

    @staticmethod

    @staticmethod




    @staticmethod



    @staticmethod





    @staticmethod



    @staticmethod




    @staticmethod

    @staticmethod





    def _record_duration_benchmark(self, job: Job, processing_seconds: float) -> None:
        try:
            if processing_seconds <= 0 or job.info.width <= 0 or job.info.height <= 0:
                return

            features = self._duration_estimation_features(job.info)


            if job.ai_info is not None and job.ai_info.fps > 0:
                features["ai_fps"] = float(self._round_fps(job.ai_info.fps))
                if job.ai_info.frames > 0:
                    features["ai_frames"] = int(job.ai_info.frames)
                features["ai_pixel_rate"] = float(features["ai_pixels"]) * float(features["ai_fps"])
                features["workload"] = float(features["ai_pixel_rate"]) * float(features["length"])


            source_content_sha256 = (job.history_source_sha256 or
                                     self._v248_source_fingerprint(job.info.path))
            configuration_sha256 = job.history_configuration_sha256
            seed_model_id = job.history_seed_model_id
            native_model_id = job.history_native_model_id
            if not configuration_sha256:
                configuration_sha256, seed_model_id, native_model_id = self._v248_configuration_signature(features)
            now = _dt.datetime.now().astimezone()
            movie_id = now.strftime("%Y%m%d_%A_%H%M%S_%f")
            try:
                file_size = max(0, int(job.info.path.stat().st_size))
            except Exception:
                file_size = 0


            seed_batch = int(job.seed_batch_used or features["seed_batch"] or 0)
            seed_overlap = int(job.seed_overlap_used or features["seed_overlap"] or 0)
            seed_batches = int(job.seed_expected_batches or features["seed_batches"] or 0)
            is_seed = features.get("algorithm") == "SeedVR2"
            ai_frame_count = int((job.ai_info.frames if job.ai_info else features.get("ai_frames", 0)) or 0)
            speed = ai_frame_count / job.stage_seedvr2_seconds if job.stage_seedvr2_seconds > 0 and ai_frame_count else 0.0

            measured_stage_total = (
                float(job.stage_probe_seconds)
                + float(job.stage_repair_seconds)
                + float(job.stage_fps_reduce_seconds)
                + float(job.stage_denoise_seconds)
                + float(job.stage_ai_seconds)
                + float(job.stage_enhancement_seconds)
                + float(job.stage_rife_seconds)
                + float(job.stage_encode_seconds)
            )
            job.stage_other_seconds = max(0.0, float(processing_seconds) - measured_stage_total)
            observed_throughput = features["workload"] / max(1e-9, processing_seconds)
            predicted = job.estimated_seconds
            raw_predicted = job.raw_estimated_seconds
            iterative_used = False
            iterative_plan_id = ""
            iterative_target_factor = 0.0
            iterative_ai_passes = 0
            row = {
                "movie_id": movie_id,
                "date_local": now.strftime("%Y-%m-%d"),
                "day_local": now.strftime("%A"),
                "time_local": now.strftime("%H:%M:%S.%f"),
                "history_schema_version": "250",
                "file_size_bytes": str(file_size),
                "file_size_mb": f"{file_size / 1_000_000.0:.6f}",
                "movie_length_seconds": f"{float(job.info.duration):.6f}",
                "source_resolution": f"{job.info.width}x{job.info.height}",
                "source_width": str(int(job.info.width)),
                "source_height": str(int(job.info.height)),
                "source_fps": str(self._round_fps(job.info.fps)),
                "source_frames": str(int(job.info.frames or 0)),
                "fps_reduce_enabled": "1" if features["reduce_enabled"] else "0",
                "fps_reduce_mode": str(features["reduce_mode"]),
                "fps_reduce_value": f"{float(features['reduce_value']):.6f}",
                "ai_input_fps": str(self._round_fps(features["ai_fps"])),
                "ai_input_frames": str(int(features["ai_frames"])),
                "scale_factor": f"{float(features['scale']):.6f}",
                "algorithm": str(features["algorithm"]),
                "algorithm_mode": str(features["mode"]),
                "ai_output_resolution": f"{features['ai_w']}x{features['ai_h']}",
                "ai_output_width": str(int(features["ai_w"])),
                "ai_output_height": str(int(features["ai_h"])),
                "ai_output_pixels_per_frame": f"{float(features['ai_pixels']):.6f}",
                "ai_pixel_rate": f"{float(features['ai_pixel_rate']):.6f}",
                "ai_workload_pixel_frames": f"{float(features['workload']):.6f}",
                "upscale_used": "1" if features["upscale_used"] else "0",
                "seed_frames_per_batch": str(seed_batch),
                "seed_overlap": str(seed_overlap),
                "seed_expected_meta_batches": str(seed_batches),
                "rife_used": "1" if features["rife_used"] else "0",
                "rife_multiplier": str(int(features["rife_multiplier"])),
                "rife_gpu_threads": str(int(features["rife_gpu_threads"])),
                "rife_input_fps": str(self._round_fps(features["rife_input_fps"])),
                "rife_output_fps": str(self._round_fps(features["rife_output_fps"])),
                "rife_input_frames": str(int(features["rife_input_frames"])),
                "rife_output_frames": str(int(features["rife_output_frames"])),
                "rife_generated_frames": str(int(features["rife_generated_frames"])),
                "rife_pixels_per_frame": f"{float(features['rife_pixels']):.6f}",
                "rife_generated_pixel_frames": f"{float(features['rife_generated_pixel_frames']):.6f}",
                "final_encode_pixel_frames": f"{float(features['final_encode_pixel_frames']):.6f}",
                "final_encoder": str(features["final_encoder"]),
                "final_quality": str(features["final_quality"]),
                "final_quality_value": str(int(features["final_quality_value"])),
                "final_encoder_threads": str(int(features["final_encoder_threads"])),
                "expected_bitrate_mbps": f"{float(features['expected_bitrate_mbps']):.6f}",
                "rife_pipeline_workload": f"{float(features['rife_pipeline_workload']):.6f}",
                "seed_nvidia_launch_mode": str(features["seed_nvidia_launch_mode"]),
                "seed_disable_dynamic_vram": "1" if features["seed_disable_dynamic_vram"] else "0",
                "seed_disable_async_offload": "1" if features["seed_disable_async_offload"] else "0",
                "repair_enabled": "1" if features["repair"] else "0",
                "denoise_setting": str(features["denoise"]),
                "color_setting": str(features["color"]),
                "brightness_setting": str(features["brightness"]),
                "white_setting": str(features["white"]),
                "output_resolution": f"{features['out_w']}x{features['out_h']}",
                "output_width": str(int(features["out_w"])),
                "output_height": str(int(features["out_h"])),
                "processing_duration_seconds": f"{float(processing_seconds):.6f}",
                "processing_duration_hms": self._fmt_prediction_duration(processing_seconds),
                "stage_probe_seconds": f"{float(job.stage_probe_seconds):.6f}",
                "stage_repair_seconds": f"{float(job.stage_repair_seconds):.6f}",
                "stage_fps_reduce_seconds": f"{float(job.stage_fps_reduce_seconds):.6f}",
                "stage_denoise_seconds": f"{float(job.stage_denoise_seconds):.6f}",
                "stage_ai_seconds": f"{float(job.stage_ai_seconds):.6f}",
                "preseed_mode": str(features.get("preseed_mode", "Only Bicubic")),
                "pre_neural_downscale_factor": f"{float(features.get('pre_neural_downscale_factor', 1.0)):.6f}",
                "pre_neural_input_pixels": f"{float(features.get('pre_neural_input_pixels', features.get('source_pixels', 0))):.6f}",
                "preseed_factor": f"{float(features.get('preseed_factor', 1.0)):.6f}",
                "seedvr2_factor": f"{float(features.get('seedvr2_factor', 1.0)):.6f}",
                "stage_pre_neural_downscale_seconds": f"{float(job.stage_pre_neural_downscale_seconds):.6f}",
                "stage_native_vsr_seconds": f"{float(job.stage_native_vsr_seconds):.6f}",
                "stage_preseed_resize_seconds": f"{float(job.stage_preseed_resize_seconds):.6f}",
                "stage_seedvr2_seconds": f"{float(job.stage_seedvr2_seconds):.6f}",
                "stage_enhancement_seconds": f"{float(job.stage_enhancement_seconds):.6f}",
                "stage_rife_seconds": f"{float(job.stage_rife_seconds):.6f}",
                "stage_encode_seconds": f"{float(job.stage_encode_seconds):.6f}",
                "stage_other_seconds": f"{float(job.stage_other_seconds):.6f}",
                "observed_workload_per_second": f"{float(observed_throughput):.9f}",
                "estimated_before_run_seconds": f"{float(predicted):.6f}" if predicted is not None else "",
                "raw_estimated_before_recalibration_seconds": f"{float(raw_predicted):.6f}" if raw_predicted is not None else "",
                "timing_recalibration_factor": f"{float(job.timing_recalibration_factor or 1.0):.6f}",
                "timing_recalibration_samples": str(int(job.timing_recalibration_samples or 0)),
                "timing_recalibration_confidence_percent": str(int(job.timing_recalibration_confidence or 0)),
                "iterative_restoration_used": "1" if iterative_used else "0",
                "iterative_restoration_plan_id": iterative_plan_id,
                "iterative_restoration_target_factor": f"{float(iterative_target_factor):.6f}",
                "iterative_restoration_ai_passes": str(int(iterative_ai_passes)),
                "prediction_similarity_percent": str(int(job.estimate_similarity or 0)),
                "estimation_error_percent": error_pct,
                "source_content_sha256": source_content_sha256,
                "source_fingerprint_schema": "sampled-sha256-v1" if source_content_sha256 else "unavailable",
                "configuration_sha256": configuration_sha256,
                "prediction_basis": str(job.prediction_basis),
                "prediction_evidence": str(job.prediction_evidence),
                "seed_model_identifier": seed_model_id,
                "native_vsr_model_identifier": native_model_id,
                "seed_requested_max_temporal_batch": job.seed_initial_batch_requested if is_seed else "",
                "seed_requested_temporal_overlap": job.seed_initial_overlap_requested if is_seed else "",
                "seed_vae_tile_pixels": str(job.seed_vae_tile_used) if is_seed and job.seed_vae_tile_used else "",
                "seed_vae_spatial_overlap_pixels": str(job.seed_vae_spatial_overlap_used) if is_seed and job.seed_vae_tile_used > 0 else "",
                "seed_requested_vae_tile": job.seed_initial_vae_tile_requested if is_seed else "",
                "seed_requested_vae_spatial_overlap": job.seed_initial_vae_overlap_requested if is_seed else "",
                "seed_attempt_count": str(job.seed_attempt_count) if is_seed else "",
                "seed_oom_retry_count": str(job.seed_oom_retry_count) if is_seed else "",
                "seed_effective_frames_per_second": f"{speed:.6f}" if is_seed and speed else "",
                "seed_peak_dedicated_vram_gb_sampled": f"{job.seed_peak_dedicated_vram_gb:.3f}" if is_seed and job.seed_peak_dedicated_vram_gb else "",
                "seed_peak_shared_gpu_gb_sampled": f"{job.seed_peak_shared_gpu_gb:.3f}" if is_seed and job.seed_peak_shared_gpu_gb else "",
                "record_type": "JOB_COMPLETE",
                "seed_run_id": job.seed_benchmark_run_id if is_seed else "",
                "seed_attempt_result": "SUCCESS" if is_seed else "",
                "seed_dynamic_vram_enabled": ("0" if features["seed_disable_dynamic_vram"] else "1") if is_seed else "",
                "seed_async_offload_enabled": ("0" if features["seed_disable_async_offload"] else "1") if is_seed else "",
                "seed_attention_backend_reported": "ComfyUI PyTorch attention; CUDA SDPA kernel unverified" if is_seed else "",
                "seed_blockswap_status": "unavailable in legacy LongVideo workflow" if is_seed else "",
                "seed_dit_compile_status": "unavailable in legacy LongVideo workflow" if is_seed else "",
            }

            with self._duration_history_lock:
                self._ensure_duration_history_file()
                with self.duration_history_path.open("a", encoding="utf-8-sig", newline="") as fh:
                    # The migrated history may include extra user-defined columns.
                    with self.duration_history_path.open("r", encoding="utf-8-sig", newline="") as hdr:
                        actual_fields = list(csv.DictReader(hdr).fieldnames or DURATION_HISTORY_COLUMNS)
                    writer = csv.DictWriter(fh, fieldnames=actual_fields, extrasaction="ignore")
                    writer.writerow(row)
                    fh.flush()
                    try:
                        os.fsync(fh.fileno())
                    except Exception:
                        pass

            self._invalidate_duration_history_cache()
            self._post(
                "log",
                f"V193 DURATION HISTORY: benchmark {movie_id}; {features['algorithm']} {features['mode']}; "
                f"source={job.info.width}x{job.info.height}@{job.info.fps:.3f}; "
                f"AI={features['ai_w']}x{features['ai_h']}@{self._round_fps(features['ai_fps'])}; "
                f"scale={features['scale']:.3f}X; RIFE={features['rife_multiplier']}X if used; "
                f"AI={self._fmt_prediction_duration(job.stage_ai_seconds)}; "
                f"RIFE={self._fmt_prediction_duration(job.stage_rife_seconds)}; "
                f"final_encoder={features['final_encoder']}/{features['final_quality']}; "
                f"encode={self._fmt_prediction_duration(job.stage_encode_seconds)}; "
                f"processing={self._fmt_prediction_duration(processing_seconds)}; history={self.duration_history_path}"
            )
        except Exception as e:
            self._post("log", f"V193 duration-history warning: could not record benchmark: {e}")


    def _section2_var_map(self) -> Dict[str, tk.Variable]:
        return {
            "fps_reduce_enable": self.fps_reduce_enable,
            "fps_reduce_mode": self.fps_reduce_mode,
            "fps_reduce_max": self.fps_reduce_max,
            "enhancement_enable": self.enhancement_enable,
            "repair_enable": self.repair_enable,
            "deinterlace_auto": self.deinterlace_auto,
            "denoise": self.denoise,
            "color_correction": self.color_correction,
            "brightness_correction": self.brightness_correction,
            "white_correction": self.white_correction,
            "sharpen": self.sharpen,
            "deband": self.deband,
            "scaling_enable": self.scaling_enable,
            "scaling1_enabled": self.scaling1_enabled,
            "scaling1_method": self.scaling1_method,
            "scaling1_factor": self.scaling1_factor,
            "scaling1_target": self.scaling1_target,
            "scaling2_enabled": self.scaling2_enabled,
            "scaling2_method": self.scaling2_method,
            "scaling2_factor": self.scaling2_factor,
            "scaling2_target": self.scaling2_target,
            "scaling3_enabled": self.scaling3_enabled,
            "scaling3_method": self.scaling3_method,
            "scaling3_factor": self.scaling3_factor,
            "scaling3_target": self.scaling3_target,
            "scaling4_target": self.scaling4_target,
            "upscale_engine": self.upscale_engine,
            "upscale_enable": self.upscale_enable,
            "downscale_enable": self.downscale_enable,
            "downscale_preset": self.downscale_preset,
            "downscale_custom": self.downscale_custom,
            "seed_upscale": self.seed_upscale,
            "seedvr2_custom_factor": self.seedvr2_custom_factor,
            "seed_target_resolution": self.seed_target_resolution,
            "seed_parameter_mode": self.seed_parameter_mode,
            "seed_batch_max": self.seed_batch_max,
            "seed_temporal_overlap": self.seed_temporal_overlap,
            "seed_vae_tile": self.seed_vae_tile,
            "seed_vae_spatial_overlap": self.seed_vae_spatial_overlap,
            "comfy_disable_dynamic_vram": self.comfy_disable_dynamic_vram,
            "comfy_disable_async_offload": self.comfy_disable_async_offload,
            "preseed_mode": self.preseed_mode,
            "preseed_resolution": self.preseed_resolution,
            "native_sr_enable": self.native_sr_enable,
            "native_sr_model": self.native_sr_model,
            "native_sr_python": self.native_sr_python,
            "native_sr_repo": self.native_sr_repo,
            "native_sr_config": self.native_sr_config,
            "native_sr_checkpoint": self.native_sr_checkpoint,
            "native_sr_max_seq_len": self.native_sr_max_seq_len,
            "native_sr_chunk_frames": self.native_sr_chunk_frames,
            "basicvsr_persistent_worker": self.basicvsr_persistent_worker,
            "basicvsr_tile_profile": self.basicvsr_tile_profile,
            "pre_neural_downscale_preset": self.pre_neural_downscale_preset,
            "pre_neural_downscale_custom": self.pre_neural_downscale_custom,
            "native_sr_preseed_preset": self.native_sr_preseed_preset,
            "native_sr_preseed_custom": self.native_sr_preseed_custom,
            "force_exact_resolution": self.force_exact_resolution,
            "rife_enable": self.rife_enable,
            "rife_mode": self.rife_mode,
            "rife_multiplier": self.rife_multiplier,
            "rife_target_fps": self.rife_target_fps,
            "rife_gpu_thread": tk.IntVar(value=RIFE_GPU_THREADS_FIXED),
            "encode_backend": self.encode_backend,
            "encode_quality": self.encode_quality,
            "x265_threads": self.x265_threads,
            "comfy_launch_mode": self.comfy_launch_mode,
        }

    @staticmethod
    def _raw_tk_value(var: tk.Variable):
        try:
            raw = var._tk.globalgetvar(var._name)
            if isinstance(var, tk.BooleanVar):
                return bool(var._tk.getboolean(raw))
            if isinstance(var, tk.IntVar):
                return int(raw)
            if isinstance(var, tk.DoubleVar):
                return float(raw)
            return str(raw)
        except Exception:
            try:
                return var.get()
            except Exception:
                return None

    def _section2_snapshot_from_ui(self) -> Dict[str, Any]:
        return {
            name: self._raw_tk_value(var)
            for name, var in self._section2_var_map().items()
        }

    def _job_setting(self, name: str, var: tk.Variable):
        ctx = self._job_settings_context
        if isinstance(ctx, Job) and name in ctx.section2_settings:
            return ctx.section2_settings[name]
        return self._raw_tk_value(var)

    def _initialize_job_section2_settings(self, job: Job) -> None:
        base = getattr(self, "_section2_template", None)
        if not isinstance(base, dict):
            base = self._section2_snapshot_from_ui()
        if not job.section2_settings:
            job.section2_settings = dict(base)

    def _initialize_section2_scoping(self) -> None:
        self._section2_syncing_selection = False
        self._section2_selection_after_id = None
        self._section2_prediction_after_id = None
        self._section2_prediction_queue = []
        self._light_preview_after_id = None
        self._section2_template = self._section2_snapshot_from_ui()
        for job in self.jobs:
            self._initialize_job_section2_settings(job)
        for name, var in self._section2_var_map().items():
            try:
                var.trace_add(
                    "write",
                    lambda *_args, setting_name=name, setting_var=var:
                        self._apply_section2_setting_immediately(setting_name, setting_var)
                )
            except Exception:
                pass
        self._update_section2_selection_status()
        self._refresh_seed_effective_preview()

    def _selected_jobs_from_table(self) -> List[Job]:
        if not hasattr(self, "tree"):
            return []
        selected_ids = set(self.tree.selection())
        return [j for j in self.jobs if j.tree_id in selected_ids]

    def _apply_section2_setting_immediately(self, name: str, var: tk.Variable) -> None:
        if getattr(self, "_section2_syncing_selection", False):
            return

        selected = self._selected_jobs_from_table()
        if not selected:
            return

        value = self._raw_tk_value(var)

        for job in selected:
            self._initialize_job_section2_settings(job)
            job.section2_settings[name] = value

            if name == "upscale_engine":
                job.engine_override = ""
            elif name == "seed_upscale":
                job.scale_choice_override = ""
            elif name == "seed_target_resolution":
                job.seed_target_resolution_override = ""
            elif name in {"fps_reduce_enable", "fps_reduce_mode", "fps_reduce_max"}:
                job.ai_fps_override = 0.0

            try:
                self._update_job_row(job)
            except Exception:
                pass

        self._update_section2_selection_status()
        if name.startswith("seed_") or name in {"upscale_engine", "seedvr2_custom_factor"}:
            self._refresh_seed_effective_preview()

        pending = getattr(self, "_section2_prediction_after_id", None)
        if pending:
            try:
                self.after_cancel(pending)
            except Exception:
                pass

        self._section2_prediction_queue = list(selected)
        self._section2_prediction_after_id = self.after(
            10, self._refresh_one_selected_section2_prediction
        )

    def _refresh_one_selected_section2_prediction(self) -> None:
        self._section2_prediction_after_id = None
        queue = getattr(self, "_section2_prediction_queue", [])
        if not queue:
            self.after_idle(self._refresh_preview)
            return

        job = queue.pop(0)
        try:
            self._update_job_duration_estimate(job, force=True)
            self._update_job_row(job)
        except Exception:
            pass

        if queue:
            self._section2_prediction_after_id = self.after(1, self._refresh_one_selected_section2_prediction)
        else:
            self._update_total_queue_estimate()
            self._guarded_section2_refresh_preview()

    def _refresh_selected_section2_predictions(self) -> None:
        self._section2_prediction_queue = list(self._selected_jobs_from_table())
        if self._section2_prediction_queue:
            self._refresh_one_selected_section2_prediction()

    def _load_section2_controls_from_job(self, job: Job) -> None:
        self._initialize_job_section2_settings(job)
        var_map = self._section2_var_map()
        self._section2_syncing_selection = True
        try:
            for name, var in var_map.items():
                if name not in job.section2_settings:
                    continue
                try:
                    desired = job.section2_settings[name]
                    current = self._raw_tk_value(var)
                    if str(current) != str(desired):
                        var.set(desired)
                except Exception:
                    pass
        finally:
            self._section2_syncing_selection = False

        self._update_fps_reduce_controls()
        self._update_rife_controls()
        self._update_enhancement_controls()
        self._update_scaling_widgets()
        self._update_upscale_controls()
        self._update_downscale_controls()
        self._sync_upscale_size_choice_from_controls()
        self._update_encode_controls()
        self._update_comfy_command_preview()
        self._guarded_section2_refresh_preview()

    def _iter_widget_descendants(self, root):
        try:
            children = root.winfo_children()
        except Exception:
            return
        for child in children:
            yield child
            yield from self._iter_widget_descendants(child)

    def _capture_section2_widget_states(self) -> None:
        if not hasattr(self, "settings_nb"):
            return
        cache = {}
        for widget in self._iter_widget_descendants(self.settings_nb):
            try:
                state = str(widget.cget("state"))
            except Exception:
                continue
            cache[widget] = state
        self._section2_widget_state_cache = cache

    def _set_section2_enabled(self, enabled: bool) -> None:
        cache = getattr(self, "_section2_widget_state_cache", None)
        if not cache:
            return
        for widget, original_state in list(cache.items()):
            try:
                if not widget.winfo_exists():
                    continue
                # The installation file inventory is global and must remain
                # accessible even when the queue has no selected row.
                ancestor = widget
                files_panel = getattr(self, "_files_global_panel", None)
                in_global_panel = False
                while ancestor is not None:
                    if ancestor is files_panel:
                        in_global_panel = True
                        break
                    ancestor = getattr(ancestor, "master", None)
                if in_global_panel:
                    continue
            except Exception:
                continue
            desired_state = original_state if enabled else "disabled"
            try:
                widget.configure(state=desired_state)
                continue
            except Exception:
                pass
            try:
                if enabled:
                    widget.state(["!disabled"])
                else:
                    widget.state(["disabled"])
            except Exception:
                pass

    def _update_section2_selection_status(self) -> None:
        if not hasattr(self, "section2_selection_text"):
            return
        selected = self._selected_jobs_from_table()
        self._set_section2_enabled(bool(selected))
        self._update_enhancement_controls()
        if selected:
            self._update_scaling_widgets()
        if not selected:
            self.section2_selection_text.set(
                "Select one or more files in Table #1. Section #2 is disabled until a row is selected."
            )
            return
        if len(selected) == 1:
            self.section2_selection_text.set(
                f"Editing: {selected[0].info.path.name} — Section #2 changes apply immediately."
            )
        else:
            self.section2_selection_text.set(
                f"Editing {len(selected)} selected files — every Section #2 change applies immediately to all selected files."
            )

    def _on_queue_selection_changed(self, _event=None) -> None:
        pending = getattr(self, "_section2_selection_after_id", None)
        if pending:
            try:
                self.after_cancel(pending)
            except Exception:
                pass
        self._section2_selection_after_id = self.after(1, self._apply_queue_selection_to_section2)

    def _apply_queue_selection_to_section2(self) -> None:
        self._section2_selection_after_id = None
        selected = self._selected_jobs_from_table()
        if selected:
            self._load_section2_controls_from_job(selected[0])
        self._update_section2_selection_status()
        self._update_upscale_controls()
        self._update_downscale_controls()
        self._update_fps_reduce_controls()
        self._update_rife_controls()
        self._update_encode_controls()
        self._refresh_seed_effective_preview()

    def _job_settings_call(self, job: Optional[Job], func, *args, **kwargs):
        previous = self._job_settings_context
        if isinstance(job, Job):
            self._job_settings_context = job
        try:
            return func(*args, **kwargs)
        finally:
            self._job_settings_context = previous

    @staticmethod
    @staticmethod
    def _engine_display_name(engine: str) -> str:
        return "SeedVR2"


    @staticmethod
    @staticmethod
    def _engine_from_table(display: str) -> str:
        return "SeedVR2"


    @staticmethod
    @staticmethod
    def _factor_editor_values(engine: str) -> Tuple[str, ...]:
        return ("1",)


    @staticmethod
    def _choice_to_editor_text(choice: str) -> str:
        raw = str(choice or "").strip()
        if raw.endswith("X"):
            return raw[:-1]
        return raw

    @staticmethod
    @staticmethod
    def _editor_text_to_choice(value: str, engine: str) -> str:
        return "1X"


    def _selected_engine(self) -> str:
        return "SeedVR2"


    def _selected_upscale_choice(self, engine: Optional[str] = None) -> str:
        return "1X"


    def _selected_pre_neural_downscale_factor(self) -> float:
        """Explicit Lanczos REDUCTION before native 4X. Never a conventional enlargement."""
        custom = str(self._job_setting("pre_neural_downscale_custom", self.pre_neural_downscale_custom) or "").strip()
        preset = str(self._job_setting("pre_neural_downscale_preset", self.pre_neural_downscale_preset) or "1.00X").strip()
        raw = custom if custom else preset
        try:
            value = float(raw.replace(",", ".").rstrip("xX"))
        except (ValueError, OverflowError):
            raise BackendError(f"Invalid pre-neural downscale {raw!r}; enter 0.10–1.00.")
        if not math.isfinite(value) or not 0.10 <= value <= 1.00:
            raise BackendError(f"Pre-neural downscale {value:g}X must be from 0.10X to 1.00X.")
        return value

    def _pre_neural_source_dimensions(self, info: VideoInfo) -> Tuple[int, int, float]:
        if self._selected_preseed_mode() == "Only Bicubic":
            return info.width, info.height, 1.0
        factor = self._selected_pre_neural_downscale_factor()
        width = self._even_dimension(info.width * factor)
        height = self._even_dimension(info.height * factor)
        if min(width, height) < 16:
            raise BackendError(
                f"Pre-neural downscale {factor:g}X leaves {width}x{height}, below 16px. "
                "Increase the factor to preserve a viable neural input.")
        if max(width * 4, height * 4) > 8192:
            raise BackendError(
                f"Native neural 4X would be {width * 4}x{height * 4} (>8192px). "
                "Reduce the pre-neural factor.")
        return width, height, factor

    def _run_pre_neural_downscale(self, job: Job, source: Path, temp_dir: Path) -> Path:
        """Resize losslessly before 4X VSR, so the neural network consumes smaller frames."""
        info = self._probe_video(source)
        w, h, factor = self._pre_neural_source_dimensions(info)
        if w == info.width and h == info.height:
            self._post("log", "V245 PRE-NEURAL DOWNSCALE: 1X; source unchanged.")
            return source
        output = Path(temp_dir) / "V245_pre_neural_downscale_lossless.mkv"
        cmd = [self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "error",
               "-i", str(source), "-map", "0:v:0", "-an", "-sn",
               "-vf", f"scale={w}:{h}:flags=lanczos,format=gbrp",
               "-c:v", "ffv1", "-level", "3", "-pix_fmt", "gbrp",
               "-fps_mode", "passthrough", str(output)]
        self._post("log", f"V245 PRE-NEURAL DOWNSCALE: {info.width}x{info.height} "
                          f"-> {w}x{h} ({factor:g}X Lanczos reduction only); "
                          f"native BasicVSR++/RealBasicVSR 4X then processes {w}x{h} input.")
        if self._run_process(cmd, job) != 0 or not output.is_file() or output.stat().st_size < 1024:
            raise BackendError("Pre-neural downscale failed. Native neural 4X was not started.")
        verify = self._probe_video(output)
        if (verify.width, verify.height) != (w, h):
            raise BackendError(f"Pre-neural geometry mismatch: {verify.width}x{verify.height} vs {w}x{h}.")
        if info.frames and verify.frames and abs(verify.frames-info.frames) > 1:
            raise BackendError(f"Pre-neural downscale changed frame count: {info.frames}->{verify.frames}.")
        if abs(verify.fps-info.fps) > 0.02:
            raise BackendError(f"Pre-neural downscale changed frame rate: {info.fps}->{verify.fps}.")
        return output

    def _selected_native_preseed_factor(self, info: Optional[VideoInfo] = None) -> float:
        if info is None:
            ctx = self._job_settings_context
            info = ctx.info if isinstance(ctx, Job) else None
        return self._four_scaling_plan(info)[1] / float(info.width) if info is not None and info.width else 1.0


    def _refresh_native_sr_scale_plan(self) -> None:
        if not hasattr(self, "native_sr_scale_plan"):
            return
        jobs = self._selected_jobs_from_table() if hasattr(self, "tree") else []
        job = jobs[0] if jobs else (self.jobs[0] if getattr(self, "jobs", None) else None)
        try:
            if job is None or job.info.width < 2 or job.info.height < 2:
                if not bool(self._raw_tk_value(self.scaling_enable)):
                    self.native_sr_scale_plan.set("UPSCALING OFF: all stages bypassed | Select a video for dimensions")
                    return
                parts = []
                for n in (1, 2, 3, 4):
                    if not bool(getattr(self, f"scaling{n}_enabled").get()):
                        parts.append(f"Stage {n} OFF")
                    else:
                        mode = getattr(self, f"scaling{n}_method").get()
                        factor = ("1X" if mode == "SeedVR2 restoration" else
                                  "4X" if mode != "Bicubic" else getattr(self, f"scaling{n}_factor").get())
                        parts.append(f"Stage {n}: {mode} {factor}")
                self.native_sr_scale_plan.set(" → ".join(parts) + " | Select a video for dimensions")
                return
            plan, w, h = self._job_settings_call(job, self._four_scaling_plan, job.info)
            summary = f"Source {job.info.width}×{job.info.height}"
            for i, (mode, factor, sw, sh) in enumerate(plan, 1):
                summary += f" → Stage {i}: " + ("OFF" if mode == "OFF" else f"{mode} ({factor:g}X)") + f" {sw}×{sh}"
            self.native_sr_scale_plan.set(summary + f" → Final {w}×{h} | Overall scaling {w/max(1, job.info.width):.3g}X")
        except BackendError as exc:
            self.native_sr_scale_plan.set(f"Upscaling configuration error: {exc}")

    def _selected_seedvr2_custom_factor(self) -> Optional[float]:
        return None


    def _selected_seed_target_resolution(self) -> str:
        return "Use upscale factor"




    def _effective_upscale_info(self, info: VideoInfo) -> VideoInfo:
        ctx = self._job_settings_context
        if not self._selected_downscale_enable():
            return info
        # The original queued VideoInfo is projected to the pre-AI resolution.
        # Actual intermediates (pre_ai_fused.mkv, AI outputs, etc.) are NEVER projected again.
        if isinstance(ctx, Job) and info is ctx.info:
            w, h = self._downscale_dimensions(info.width, info.height)
            projected = copy.copy(info)
            projected.width = w
            projected.height = h
            return projected
        return info

    @staticmethod
    def _format_scale_factor_value(factor: float) -> str:
        value = float(factor)
        rounded = round(value)
        if abs(value - rounded) < 1e-9:
            return str(int(rounded))
        return f"{value:g}"








    def _is_factor_4k_limited(self, info: VideoInfo, engine: Optional[str] = None, choice: Optional[str] = None) -> bool:
        return False


    def _factor_for(self, info: VideoInfo, engine: Optional[str] = None, choice: Optional[str] = None) -> float:
        _plan, w, h = self._four_scaling_plan(self._effective_upscale_info(info))
        return w / float(info.width) if info.width else 1.0


    def _seed_ai_factor_for(self, info: VideoInfo, requested_factor: Optional[float] = None) -> float:
        requested = float(
            requested_factor
            if requested_factor is not None
            else self._factor_for(info, "SeedVR2")
        )
        return max(1.0, min(12.0, requested))

    @staticmethod
    def _even_dimension(value: float) -> int:
        return max(2, int(round(float(value) / 2.0) * 2))


    def _exact_target_geometry(self, info: VideoInfo) -> Optional[Tuple[int, int]]:
        # Native SeedVR2 performs its required preprocessing inside the workflow.
        # Final encoding is forbidden from any additional spatial enlargement.
        return None

    def _needs_exact_resize(self, info: VideoInfo) -> bool:
        return False

    def _exact_scale_filter_args(self, info: VideoInfo) -> List[str]:
        return []


    def _output_geometry(self, info: VideoInfo) -> Tuple[int, int, float, float]:
        source = self._effective_upscale_info(info)
        _stages, width, height = self._four_scaling_plan(source)
        fps, _mode, _value, _applied = self._fps_reduction_plan(source)
        fps = fps if fps > 0 else source.fps
        _use_rife, _mult, fps = self._rife_plan_for_fps(fps)
        return width, height, fps, width / max(1.0, source.width)


    def _planned_geometry_text(self, info: VideoInfo) -> str:
        w, h, fps, factor = self._output_geometry(info)
        plans, _w, _h = self._four_scaling_plan(info)
        stage_text = " → ".join(f"Stage {i}: " + ("OFF" if name == "OFF" else f"{name} {scale:.3g}X")
                                for i, (name, scale, _, _) in enumerate(plans, 1))
        return f"{info.width}×{info.height} → {stage_text} → {w}×{h} @ {self._fmt_fps(fps)}fps (total {factor:.3g}X)"

    def _refresh_preview(self):
        self._refresh_seed_effective_preview()
        self._refresh_temp_space_prediction()
        self._update_downscale_controls()
        self._refresh_native_sr_scale_plan()
        selected = self._selected_jobs_from_table()
        job = selected[0] if selected else (self.jobs[0] if self.jobs else None)
        if job is None:
            self.fps_reduce_preview.set("")
            self.geometry_preview.set("Select a video to preview the four-stage upscaling pipeline.")
            return
        info = job.info
        try:
            ai_fps, _mode, limit, reduced = self._job_settings_call(job, self._fps_reduction_plan, info)
            self.fps_reduce_preview.set(
                f"FPS Reduce: {self._fmt_fps(info.fps)} → {self._fmt_fps(ai_fps)} FPS (limit {limit:g})"
                if reduced else f"FPS Reduce: Off ({self._fmt_fps(info.fps)} FPS)"
            )
            w, h, fps, factor = self._job_settings_call(job, self._output_geometry, info)
            stages, _w, _h = self._job_settings_call(job, self._four_scaling_plan, info)
            display = f"{info.width}×{info.height}"
            for index, (method, scale, stage_w, stage_h) in enumerate(stages, start=1):
                display += (f" → Stage {index}: OFF ({stage_w}×{stage_h})" if method == "OFF"
                            else f" → Stage {index}: {method} {scale:g}X ({stage_w}×{stage_h})")
            display += f" → {w}×{h} {self._fmt_fps(fps)}fps (total {factor:.3g}X)"
            self.geometry_preview.set(display)
            b = self._quality_bitrate(w, h, fps)
            quality = self._job_settings_call(job, self._selected_encode_quality)
            backend = self._job_settings_call(job, self._selected_encode_backend)
            setting = (f"CQ {NVENC_CQ_VALUES[quality]} | p7" if backend == "NVIDIA NVENC (fast)"
                       else f"CRF {X265_CRF_VALUES[quality]} | slow")
            self.auto_bitrate_preview.set(
                f"Expected bitrate ({quality}): ~{b:.2f} Mb/s at {w}×{h} / {self._fmt_fps(fps)} FPS | "
                f"{backend} | {setting} | HEVC 10-bit | MP4"
            )
        except BackendError as exc:
            self.geometry_preview.set(f"Invalid scaling configuration: {exc}")


    @staticmethod
    def _interp(x: float, points: List[Tuple[float, float]]) -> float:
        points = sorted(points)
        if x <= points[0][0]:
            x0, y0 = points[0]
            return max(0.5, y0 * x / x0)
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            if x <= x1:
                t = (x - x0) / max(1e-9, x1 - x0)
                return y0 + t * (y1 - y0)
        x0, y0 = points[-1]
        return y0 * (x / x0) ** 0.65

    def _selected_encode_backend(self) -> str:
        backend = str(self._job_setting("encode_backend", self.encode_backend) or "NVIDIA NVENC (fast)")
        return backend if backend in ENCODE_BACKENDS else "NVIDIA NVENC (fast)"

    def _selected_encode_quality(self) -> str:
        backend = self._selected_encode_backend()
        allowed = NVENC_QUALITY_PRESETS if backend == "NVIDIA NVENC (fast)" else X265_QUALITY_PRESETS
        quality = str(self._job_setting("encode_quality", self.encode_quality) or "Medium")
        return quality if quality in allowed else "Medium"

    def _selected_x265_threads(self) -> int:
        maximum = max(1, int(os.cpu_count() or 1))
        try:
            value = int(self._job_setting("x265_threads", self.x265_threads))
        except Exception:
            value = min(12, maximum)
        return max(1, min(maximum, value))

    def _update_encode_controls(self) -> None:
        if not hasattr(self, "encode_quality_box"):
            return
        backend = str(self._raw_tk_value(self.encode_backend) or "NVIDIA NVENC (fast)")
        if backend not in ENCODE_BACKENDS:
            backend = "NVIDIA NVENC (fast)"
        if backend == "NVIDIA NVENC (fast)":
            allowed = NVENC_QUALITY_PRESETS
            self.x265_threads_spin.configure(state="disabled")
        else:
            allowed = X265_QUALITY_PRESETS
            self.x265_threads_spin.configure(state="readonly")
        self.encode_quality_box.configure(values=allowed)
        current_quality = str(self._raw_tk_value(self.encode_quality) or "Medium")
        if current_quality not in allowed:
            self.encode_quality.set("Medium")
        self._refresh_preview()

    def _quality_bitrate(self, width: int, height: int, fps: float) -> float:
        width = max(2, int(width or 0))
        height = max(2, int(height or 0))
        fps = max(1.0, float(fps or 0.0))
        pixels = float(width * height)
        anchors = [
            (1280.0 * 720.0, 2.5),
            (1920.0 * 1080.0, 4.0),
            (2560.0 * 1440.0, 6.0),
            (3840.0 * 2160.0, 10.0),
        ]
        base = self._interp(pixels, anchors)
        if fps <= 30.0:
            fps_factor = 1.0
        elif fps <= 60.0:
            fps_factor = fps / 30.0
        else:
            fps_factor = 2.0 * (fps / 60.0) ** 0.5
        quality = self._selected_encode_quality()
        if self._selected_encode_backend() == "NVIDIA NVENC (fast)":
            quality_factor = NVENC_EXPECTED_BITRATE_MULTIPLIERS[quality]
        else:
            quality_factor = X265_EXPECTED_BITRATE_MULTIPLIERS[quality]
        return max(0.6, base * fps_factor * quality_factor)


    def _set_processing_highlight(self, mode: str) -> None:
        neutral = PASTEL["green"]
        magenta = "#FF00FF"
        start_color = magenta if mode == "processing" else neutral
        pause_color = magenta if mode == "paused" else neutral
        try:
            self.start_highlight_frame.configure(bg=start_color)
        except Exception:
            pass
        try:
            self.pause_highlight_frame.configure(bg=pause_color)
        except Exception:
            pass

    @staticmethod
    def _format_decimal_gb(value: float) -> str:
        value = max(0.0, float(value or 0.0))
        if value >= 1000.0:
            return f"{value / 1000.0:.2f} TB"
        if value >= 100.0:
            return f"{value:.0f} GB"
        return f"{value:.1f} GB"

    @staticmethod
    def _existing_parent(path: Path) -> Path:
        p = Path(path)
        while not p.exists() and p.parent != p:
            p = p.parent
        return p

    def _temporary_space_for_job_gb(self, job: Job) -> float:
        duration = max(0.0, float(job.info.duration or 0.0))
        return (duration / 3600.0) * TEMP_SPACE_GB_PER_MOVIE_HOUR

    def _temporary_space_summary(self) -> Tuple[float, Optional[Job], Optional[float], List[Tuple[Job, float, Optional[float], Path]]]:
        rows: List[Tuple[Job, float, Optional[float], Path]] = []
        candidates = [job for job in self.jobs if float(job.info.duration or 0.0) > 0]
        for job in candidates:
            required = self._temporary_space_for_job_gb(job)
            temp_root = self._job_dirs(job)[3]
            probe_root = self._existing_parent(temp_root)
            free_gb: Optional[float] = None
            try:
                free_gb = float(shutil.disk_usage(probe_root).free) / 1_000_000_000.0
            except Exception:
                free_gb = None
            rows.append((job, required, free_gb, temp_root))
        if not rows:
            return 0.0, None, None, rows
        peak_row = max(rows, key=lambda item: item[1])
        return peak_row[1], peak_row[0], peak_row[2], rows

    def _refresh_temp_space_prediction(self) -> None:
        if not hasattr(self, "temp_space_prediction"):
            return
        peak_gb, peak_job, free_gb, rows = self._temporary_space_summary()
        if peak_job is None:
            self.temp_space_prediction.set(
                f"Predicted temporary space: scan videos to calculate queue peak | budget {TEMP_SPACE_GB_PER_MOVIE_HOUR:.0f} GB per movie-hour"
            )
            return
        duration_text = self._fmt_prediction_duration(float(peak_job.info.duration or 0.0))
        text = (
            f"Predicted temporary space (queue peak): ~{self._format_decimal_gb(peak_gb)} "
            f"for {peak_job.info.path.name} ({duration_text}) | budget {TEMP_SPACE_GB_PER_MOVIE_HOUR:.0f} GB/hour | "
            f"one active job; obsolete temporary videos auto-deleted when safe; final MP4 files are not included"
        )
        if free_gb is not None:
            text += f" | free on destination drive: {self._format_decimal_gb(free_gb)}"
            if free_gb < peak_gb:
                text += " | WARNING: predicted temporary space exceeds free space"
        self.temp_space_prediction.set(text)

    def _check_temp_space_before_start(self) -> bool:
        peak_gb, peak_job, _free_gb, rows = self._temporary_space_summary()
        if peak_job is None:
            return True
        shortages = []
        for job, required, free_gb, temp_root in rows:
            if free_gb is not None and required > free_gb:
                shortages.append((job, required, free_gb, temp_root))
        if not shortages:
            self._post(
                "log",
                f"V137 TEMP SPACE: predicted queue peak ~{self._format_decimal_gb(peak_gb)} using the conservative "
                f"{TEMP_SPACE_GB_PER_MOVIE_HOUR:.0f} GB/hour temporary-video budget."
            )
            return True
        worst = max(shortages, key=lambda item: item[1] - float(item[2] or 0.0))
        job, required, free_gb, temp_root = worst
        return bool(messagebox.askyesno(
            APP_NAME,
            f"Predicted temporary space is larger than available free space.\n\n"
            f"Movie: {job.info.path.name}\n"
            f"Predicted temporary peak: {self._format_decimal_gb(required)}\n"
            f"Free space: {self._format_decimal_gb(float(free_gb or 0.0))}\n"
            f"Temporary folder: {temp_root}\n\n"
            f"The estimate uses {TEMP_SPACE_GB_PER_MOVIE_HOUR:.0f} GB per movie-hour and assumes one active queue job at a time. "
            "Continue anyway?"
        ))

    def _delete_consumed_temp_video(self, path: Path, temp_dir: Path, label: str) -> None:
        p = Path(path)
        try:
            if not p.is_file():
                return
            p.resolve().relative_to(Path(temp_dir).resolve())
        except Exception:
            return
        try:
            p.unlink()
            self._post("log", f"V137 TEMP CLEANUP: deleted consumed {label}: {p}")
        except Exception as e:
            self._post("log", f"V137 TEMP CLEANUP WARNING: could not delete consumed {label}: {p}: {e}")

    def _start_queue(self):
        if self.worker and self.worker.is_alive():
            return
        if not self.jobs:
            messagebox.showwarning(APP_NAME, "The queue is empty.")
            return
        if not self._basic_validate():
            return
        self._refresh_temp_space_prediction()
        if not self._check_temp_space_before_start():
            return

        self._run_engine = self._job_setting("upscale_engine", self.upscale_engine)
        self._run_upscale_enable = self._selected_upscale_enable()
        self._run_seed_upscale = self._job_setting("seed_upscale", self.seed_upscale)
        self._run_seed_target_resolution = self._job_setting("seed_target_resolution", self.seed_target_resolution)
        
        self._run_fps_reduce_enable = bool(self._job_setting("fps_reduce_enable", self.fps_reduce_enable))
        self._run_fps_reduce_mode = str(self._job_setting("fps_reduce_mode", self.fps_reduce_mode))
        self._run_fps_reduce_max = float(self._job_setting("fps_reduce_max", self.fps_reduce_max))
        self._run_rife_enable = bool(self._job_setting("rife_enable", self.rife_enable))
        self._run_rife_mode = str(self._job_setting("rife_mode", self.rife_mode))
        self._run_rife_multiplier = str(self._job_setting("rife_multiplier", self.rife_multiplier))
        self._run_rife_target_fps = float(self._job_setting("rife_target_fps", self.rife_target_fps))
        self._run_move_processed_enable = bool(self.move_processed_enable.get())
        self._run_move_success_folder = str(self.move_success_folder.get()).strip() or DEFAULT_SUCCESS_FOLDER
        self._run_move_failed_folder = str(self.move_failed_folder.get()).strip() or DEFAULT_FAILED_FOLDER
        self._run_comfy_launch_mode = self._job_setting("comfy_launch_mode", self.comfy_launch_mode).strip() or "NVIDIA Fast"
        self._run_comfy_disable_dynamic_vram = bool(self.comfy_disable_dynamic_vram.get())
        self._run_comfy_disable_async_offload = bool(self.comfy_disable_async_offload.get())
        locked_choice = self._selected_upscale_choice(self._run_engine)
        self._log(
            f"V137 RUN PLAN LOCKED: upscale={'ON' if self._run_upscale_enable else 'OFF'}; default engine={self._run_engine}; default choice={locked_choice}; "
            f"SeedVR2 restoration scale=fixed 1X; "
            f"FPS Reduce={self._run_fps_reduce_enable}/{self._run_fps_reduce_mode}/{self._run_fps_reduce_max:g}; "
            f"RIFE={self._run_rife_enable}/{self._run_rife_mode}/{self._run_rife_multiplier}/target={self._run_rife_target_fps:g} FPS; "
            f"ComfyUI={self._run_comfy_launch_mode}; "
            f"DynamicVRAM={'OFF' if self._run_comfy_disable_dynamic_vram else 'ON'}; "
            f"async offload={'OFF' if self._run_comfy_disable_async_offload else 'ON'}; "
            f"Move source={self._run_move_processed_enable}; success='{self._run_move_success_folder}'; failed='{self._run_move_failed_folder}'."
        )
        self.stop_event.clear()
        self.pause_event.clear()
        self._save_exit_requested = False
        self._save_exit_checkpoint_in_progress = False

        self._paused_process_pids = []
        self._pause_started_at = None
        self.overall_progress.set(0)
        self.file_progress.set(0)
        for j in self.jobs:
            if j.status in ("Failed", "Done", "Stopped"):
                j.status = "Queued"
                j.stage = "waiting"
                j.progress = 0
                j.eta = "--"
                j.error = ""
                j.pre_run_overhead_seconds = 0.0
                j.started_at = 0.0
                j.elapsed_seconds = 0.0
                j.elapsed_text = "--"
                j.elapsed_display_bucket = -1
                j.ai_info = None
                j.fps_reduce_applied = False
                j.seed_batch_used = 0
                j.seed_overlap_used = 0
                j.seed_expected_batches = 0
                self._update_job_row(j)


        self._normalize_processing_order()


        self._refresh_duration_estimates()
        self.start_btn.configure(state="disabled", text="PROCESSING", style="Start.TButton")
        self._set_processing_highlight("processing")
        self.stop_btn.configure(state="normal")
        self.pause_btn.configure(state="normal", text="PAUSE", style="Pause.TButton")
        self.resume_btn.configure(state="disabled")
        self.save_exit_btn.configure(state="disabled", style="SaveExit.TButton")
        self.worker = threading.Thread(target=self._queue_worker, daemon=True)
        self.worker.start()

    def _queue_worker(self):
        try:
            self._wait_if_paused()


            prelaunch_seconds = 0.0
            seed_needed = any(
                self._job_settings_call(
                    j,
                    lambda job=j: self._selected_engine() == "SeedVR2" and self._factor_for(job.info) >= 1,
                )
                for j in self.jobs
            )
            if seed_needed and self.jobs:
                first_job = self._ordered_jobs()[0]
                first_needs_native_vsr = self._job_settings_call(
                    first_job,
                    lambda: self._selected_engine() == "SeedVR2"
                            and self._selected_preseed_mode() != "Only Bicubic",
                )
                if first_needs_native_vsr:
                    seed_needed = False
                    self._post("log", "V246 GPU RESERVATION: delaying hidden ComfyUI "
                                      "startup until after first movie's native VSR stage.")
            if seed_needed:
                _prelaunch_t0 = time.time()
                self._ensure_hidden_comfy()
                prelaunch_seconds = max(0.0, time.time() - _prelaunch_t0)
            run_jobs = self._ordered_jobs()
            total = len(run_jobs)
            had_failures = False
            if run_jobs and prelaunch_seconds > 0:
                run_jobs[0].pre_run_overhead_seconds = prelaunch_seconds

            self._post(
                "log",
                "V137 PROCESSING ORDER: "
                + ", ".join(
                    f"{j.process_order}:{j.info.path.name}" for j in run_jobs
                )
            )

            for run_idx, job in enumerate(run_jobs):
                if self.stop_event.is_set():
                    break
                self._wait_if_paused()


                self.current_job_index = self.jobs.index(job)
                self._job_settings_context = job
                self._post(
                    "current_file",
                    f"Current file: {run_idx+1} / {total} "
                    f"(order {job.process_order}) - {job.info.path.name}",
                )
                try:
                    self._process_job(job)


                    actual_processing_seconds = max(
                        0.0,
                        time.time() - job.started_at + float(job.pre_run_overhead_seconds or 0.0),
                    )
                    self._record_duration_benchmark(job, actual_processing_seconds)

                    job.elapsed_seconds = actual_processing_seconds
                    job.elapsed_text = self._fmt_elapsed_duration(
                        actual_processing_seconds
                    )
                    job.elapsed_display_bucket = int(
                        actual_processing_seconds // 60
                    )

                    job.status = "Done"
                    job.stage = "complete"
                    job.progress = 100.0
                    job.eta = "00:00"
                    self._recalibrate_queued_duration_estimates_after_actual(job, actual_processing_seconds)
                    self._move_source_after_processing(job, success=True)
                    self._post("job", job)


                    self._post("file_progress", 100.0)
                    self._post("eta", "ETA: 00:00")
                    self._post("step", "Current step: complete")


                    self._post("refresh_preview", None)
                except Cancelled:
                    final_elapsed = self._job_elapsed_now(job)
                    job.elapsed_seconds = final_elapsed
                    job.elapsed_text = self._fmt_elapsed_duration(final_elapsed)
                    job.elapsed_display_bucket = int(final_elapsed // 60)
                    job.status = "Stopped"
                    job.stage = "stopped"
                    self._post("job", job)
                    break
                except Exception as e:
                    had_failures = True
                    self._post("log", f"V141 JOB EXCEPTION: {job.info.path.name}: {e}\n{traceback.format_exc()}")
                    final_elapsed = self._job_elapsed_now(job)
                    job.elapsed_seconds = final_elapsed
                    job.elapsed_text = self._fmt_elapsed_duration(final_elapsed)
                    job.elapsed_display_bucket = int(final_elapsed // 60)
                    job.status = "Failed"
                    job.stage = "failed"
                    job.error = str(e)
                    self._post("job", job)
                    self._write_error_log(job, e)
                    failed_name = job.info.path.name
                    self._post("log", f"ERROR: {failed_name}: {e}\nContinuing with next file.")
                    self._move_source_after_processing(job, success=False)
                    self._post("job", job)
                finally:
                    self._job_settings_context = None
                    self._post(
                        "overall",
                        (run_idx + 1) / max(1, total) * 100.0,
                    )
            if self.stop_event.is_set():
                self._post("status", "Queue stopped")
                self._post("queue_finished_ui", False)
            elif had_failures:
                self._post("status", "Queue finished with errors")
                self._post("queue_finished_ui", False)
                self._post("step", "Current step: FAILED - no final output was created for failed job(s)")
            else:
                self._post("status", "Queue finished")
                self._post("queue_finished_ui", True)
        except Exception as e:
            self._post("log", f"V137 QUEUE EXCEPTION: {e}\n{traceback.format_exc()}")
            self._post("status", "Queue failed")
            self._post("queue_finished_ui", False)
        finally:


            self._stop_managed_comfy(
                reason="V62 queue boundary: stopping any remaining owned ComfyUI backend.",
                wait_port=True,
            )
            self._cleanup_retained_comfy_inputs()
            self.current_job_index = -1
            self._job_settings_context = None
            self._run_engine = None
            self._run_upscale_enable = None
            self._run_seed_upscale = None
            self._run_seed_target_resolution = None
            
            self._run_fps_reduce_enable = None
            self._run_fps_reduce_mode = None
            self._run_fps_reduce_max = None
            self._run_rife_enable = None
            self._run_rife_mode = None
            self._run_rife_multiplier = None
            self._run_rife_target_fps = None
            self._run_move_processed_enable = None
            self._run_move_success_folder = None
            self._run_move_failed_folder = None
            self._run_comfy_launch_mode = None
            self._run_comfy_disable_dynamic_vram = None
            self._run_comfy_disable_async_offload = None
            self._post("refresh_preview", None)
            self._post("worker_done", None)

    def _process_job(self, job: Job):
        self._wait_if_paused()
        engine_for_job = self._selected_engine()
        choice_for_job = self._selected_upscale_choice(engine_for_job)
        ai_fps_for_job = self._fps_reduction_plan(job.info)[0]
        self._post(
            "log",
            f"V137 BEGIN JOB: {job.info.path}; engine={self._engine_display_name(engine_for_job)}; "
            f"factor choice={choice_for_job}; FPS for AI={self._fmt_fps(ai_fps_for_job)}."
        )
        job.started_at = time.time()
        job.status = "Running"
        job.eta = "--"
        job.elapsed_seconds = float(job.pre_run_overhead_seconds or 0.0)
        job.elapsed_text = self._fmt_elapsed_duration(job.elapsed_seconds)
        job.elapsed_display_bucket = int(job.elapsed_seconds // 60)
        job.stage_probe_seconds = 0.0
        job.stage_repair_seconds = 0.0
        job.deinterlace_applied = False
        job.deinterlace_diagnostic = ""
        job.stage_fps_reduce_seconds = 0.0
        job.stage_denoise_seconds = 0.0
        job.stage_ai_seconds = 0.0
        job.stage_pre_neural_downscale_seconds = 0.0
        job.stage_native_vsr_seconds = 0.0
        job.native_vsr_frames_done = 0
        job.native_vsr_frames_expected = 0
        job.native_vsr_stage_eta_seconds = None
        job.native_vsr_eta_reference_elapsed = 0.0
        job.stage_preseed_resize_seconds = 0.0
        job.stage_seedvr2_seconds = 0.0
        job.seed_initial_batch_requested = ""
        job.seed_initial_overlap_requested = ""
        job.seed_initial_vae_tile_requested = ""
        job.seed_initial_vae_overlap_requested = ""
        job.seed_vae_tile_used = 0
        job.seed_vae_spatial_overlap_used = 0
        job.seed_attempt_count = 0
        job.seed_oom_retry_count = 0
        job.seed_benchmark_run_id = ""
        job.seed_peak_dedicated_vram_gb = 0.0
        job.seed_peak_shared_gpu_gb = 0.0
        job.stage_enhancement_seconds = 0.0
        job.stage_rife_seconds = 0.0
        job.stage_encode_seconds = 0.0
        job.stage_other_seconds = 0.0
        job.verified_ai_output_width = 0
        job.verified_ai_output_height = 0
        self._post("job", job)
        self._post("eta", "ETA: --")
        self._post("file_progress", 0.0)

        roots = self._job_dirs(job)
        final_root, repaired_dir, logs_dir, temp_root = roots
        job.output_root = final_root
        for d in roots:
            d.mkdir(parents=True, exist_ok=True)
        resume_data = {}
        run_id = uuid.uuid4().hex[:8]
        temp_name = self._v263_safe_component(
            temp_root, self._safe_stem(job.info.path.stem), f"_{run_id}",
            identity=str(job.info.path) + ':' + run_id,
            max_full_length=195, max_component_length=52,
        )
        temp_dir = temp_root / temp_name
        temp_dir.mkdir(parents=True, exist_ok=True)
        self._post("temp", f"Temporary files: {temp_dir} (deleted only after a successful completed output)")
        stamp = f"{_dt.datetime.now():%Y%m%d_%H%M%S}"
        log_name = self._v263_safe_component(
            logs_dir, self._safe_stem(job.info.path.stem), f"_{stamp}.log",
            identity=str(job.info.path), max_full_length=235, max_component_length=190,
        )
        logfile = logs_dir / log_name
        self.active_log_path = logfile
        job_completed = False
        try:
            self._set_stage(job, "probing", 0.0, 0.00, 0.03)
            stage_clock = self._job_elapsed_now(job)
            queued_info = job.info
            info = self._probe_video_resilient(
                queued_info.path,
                fallback=queued_info,
                context="queued source",
            )
            job.info = info
            job.stage_probe_seconds = max(0.0, self._job_elapsed_now(job) - stage_clock)
            self._set_stage_fraction(job, 1.0)

            self._set_stage(job, "repairing", 0.0, 0.03, 0.09)
            stage_clock = self._job_elapsed_now(job)
            if self._enhancement_is_enabled() and self._job_setting("repair_enable", self.repair_enable):
                working = self._repair_auto(job, repaired_dir)
            else:
                working = job.info.path
                self._post("log", "Automatic repair bypassed: " +
                           ("Enhancement master switch OFF." if not self._enhancement_is_enabled()
                            else "Repair option OFF."))
            job.stage_repair_seconds = max(0.0, self._job_elapsed_now(job) - stage_clock)
            self._set_stage_fraction(job, 1.0)

            audio_master = working

            self._set_stage(job, "Pre-AI deinterlace / enhancement", 0.0, 0.09, 0.105)
            stage_clock = self._job_elapsed_now(job)
            working, job.ai_info, fps_applied, denoise_applied = self._preprocess_pre_ai_fused(job, working, temp_dir)
            job.fps_reduce_applied = bool(fps_applied)
            preprocess_elapsed = max(0.0, self._job_elapsed_now(job) - stage_clock)
            applied_count = int(bool(fps_applied)) + int(bool(denoise_applied))
            if applied_count <= 0:
                job.stage_fps_reduce_seconds = 0.0
                job.stage_denoise_seconds = 0.0
            elif applied_count == 1:
                job.stage_fps_reduce_seconds = preprocess_elapsed if fps_applied else 0.0
                job.stage_denoise_seconds = preprocess_elapsed if denoise_applied else 0.0
            else:
                job.stage_fps_reduce_seconds = preprocess_elapsed / 2.0
                job.stage_denoise_seconds = preprocess_elapsed / 2.0
            self._set_stage_fraction(job, 1.0)

            scaling_is_on = bool(self._job_setting("scaling_enable", self.scaling_enable))
            self._set_stage(job, "Upscaling 1/4 → 2/4 → 3/4 → 4/4" if scaling_is_on else "Upscaling OFF (bypassed)",
                            0.0, 0.25, 0.55)
            pre_scaling = self._probe_video(Path(working))
            working = self._run_four_scaling_stages(job, Path(working), temp_dir)
            job.ai_info = self._probe_video(working)
            planned, expect_w, expect_h = self._four_scaling_plan(pre_scaling)
            if (job.ai_info.width, job.ai_info.height) != (expect_w, expect_h):
                raise BackendError("The four scaling stages did not produce their expected resolution.")
            factor = expect_w / max(1.0, float(pre_scaling.width))

            did_ai = self._selected_upscale_enable()
            job.stage_ai_seconds = float(job.stage_seedvr2_seconds + job.stage_native_vsr_seconds)
            self._post("log", f"V264 UPSCALING COMPLETE: SeedVR2 selected={did_ai}; "
                              f"SeedVR2 time={job.stage_seedvr2_seconds:.1f}s; "
                              f"neural 4X time={job.stage_native_vsr_seconds:.1f}s; no implicit restoration pass.")

            output_filters: List[str] = []
            if not self._enhancement_is_enabled():
                self._post("log", "V261 ENHANCEMENT OFF: skipping Repair, Deinterlace, Denoise, "
                                  "Color, Brightness, White balance, Sharpen and Deband. FPS Reduce unaffected.")
            if self._enhancement_is_enabled() and (
                self._job_setting("color_correction", self.color_correction) != "Off"
                or self._job_setting("brightness_correction", self.brightness_correction) != "Off"
                or self._job_setting("white_correction", self.white_correction) != "Off"
                or self._job_setting("sharpen", self.sharpen) != "Off"
                or self._job_setting("deband", self.deband) != "Off"
            ):
                self._set_stage(job, "Enhancement", 0.0, 0.80 if did_ai else 0.25, 0.07)
                stage_clock = self._job_elapsed_now(job)
                output_filters = self._prepare_output_correction_filters(job, working)
                job.stage_enhancement_seconds = max(0.0, self._job_elapsed_now(job) - stage_clock)
                self._set_stage_fraction(job, 1.0)

            ai_ref = job.ai_info or job.info
            do_rife, _job_rife_mult, _job_rife_fps = self._rife_plan_for_fps(ai_ref.fps)
            if do_rife:
                self._set_stage(job, "RIFE", 0.0, 0.80 if did_ai else 0.25, 0.15 if did_ai else 0.55)
                stage_clock = self._job_elapsed_now(job)
                final = self._rife_and_encode(job, working, audio_master, final_root, temp_dir, extra_video_filters=output_filters)
                job.stage_rife_seconds = max(0.0, self._job_elapsed_now(job) - stage_clock)
                self._set_stage_fraction(job, 1.0)
            else:
                self._set_stage(job, "encoding", 0.0, 0.95 if did_ai else 0.80, 0.05 if did_ai else 0.20)
                stage_clock = self._job_elapsed_now(job)
                final = self._final_encode(job, working, audio_master, final_root, extra_video_filters=output_filters)
                job.stage_encode_seconds = max(0.0, self._job_elapsed_now(job) - stage_clock)
                self._set_stage_fraction(job, 1.0)
            job.final_path = final
            self._post("log", f"DONE: {final}")
            job_completed = True
        finally:
            if job_completed:
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    self._post("log", f"Temporary files deleted after successful completion: {temp_dir}")
                except Exception:
                    pass
                self._post("temp", "Temporary files: none (successful job temp deleted)")
            else:
                self._post(
                    "log",
                    f"V141 RECOVERY: job did not complete successfully; temporary/intermediate files were PRESERVED: {temp_dir}"
                )
                self._post("temp", f"Recovery files preserved: {temp_dir}")
            self.active_log_path = None


    def _validate_not_black_video(self, path: Path, label: str) -> None:
        p = Path(path)
        info = self._probe_video(p)
        duration = max(0.0, float(info.duration or 0.0))
        positions = [0.02, 0.15, 0.33, 0.50, 0.67, 0.85, 0.98]
        if duration <= 0.25:
            positions = [0.0]

        frame_means = []
        frame_p99 = []
        frame_nonblack = []
        ffmpeg = self._tool(self.ffmpeg.get())

        for frac in positions:
            self._wait_if_paused()
            if self.stop_event.is_set():
                raise Cancelled()

            ss = 0.0 if duration <= 0.25 else max(0.0, min(duration - 0.05, duration * frac))
            cmd = [
                ffmpeg,
                "-hide_banner",
                "-loglevel", "error",
                "-ss", f"{ss:.6f}",
                "-i", str(p),
                "-map", "0:v:0",
                "-frames:v", "1",
                "-vf", "scale=64:64:flags=bilinear,format=gray",
                "-f", "rawvideo",
                "pipe:1",
            ]
            cp = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=self._no_window(),
            )
            raw = cp.stdout or b""
            if cp.returncode != 0 or len(raw) < 1024:
                continue

            vals = sorted(raw)
            n = len(vals)
            frame_means.append(sum(vals) / float(n))
            frame_p99.append(vals[min(n - 1, int(n * 0.99))])
            frame_nonblack.append(sum(1 for v in vals if v > 10) / float(n))

        if not frame_means:
            self._post(
                "log",
                f"V162 BLACK-FRAME GUARD: could not sample {label}; continuing because no reliable luminance samples were available."
            )
            return

        mean_peak = max(frame_means)
        p99_peak = max(frame_p99)
        nonblack_peak = max(frame_nonblack)

        self._post(
            "log",
            f"V162 BLACK-FRAME GUARD: {label}; sampled={len(frame_means)}; "
            f"peak_mean={mean_peak:.2f}; peak_p99={p99_peak}; "
            f"peak_nonblack_fraction={nonblack_peak:.5f}."
        )

        effectively_black = (
            mean_peak <= 3.0
            and p99_peak <= 12
            and nonblack_peak <= 0.005
        )

        if effectively_black:
            raise BackendError(
                f"{label} is effectively black or contains only tiny isolated bright/color artifacts. "
                "Processing is stopped before downstream stages so a near-black final movie is not accepted."
            )

    def _preserve_seedvr2_output_for_downstream(
        self,
        job: Job,
        seed_output: Path,
        temp_dir: Path,
        factor: float,
    ) -> Path:
        self._wait_if_paused()

        src = Path(seed_output)
        if not src.is_file():
            raise BackendError(
                f"SeedVR2 produced an output path, but the file no longer exists "
                f"before downstream preservation: {src}"
            )

        suffix = src.suffix.lower()
        if suffix not in VIDEO_EXTENSIONS:
            suffix = ".mkv"

        dst = temp_dir / f"seedvr2_verified_for_downstream{suffix}"
        last_error: Optional[Exception] = None

        for attempt in range(1, 16):
            self._wait_if_paused()
            if self.stop_event.is_set():
                raise Cancelled()

            partial: Optional[Path] = None
            try:
                temp_dir.mkdir(parents=True, exist_ok=True)
                partial = temp_dir / f".seedvr2_copy_{uuid.uuid4().hex[:10]}.part{suffix}"

                before = src.stat()
                if before.st_size <= 1024:
                    raise BackendError(
                        f"SeedVR2 output is unexpectedly small before preservation "
                        f"({before.st_size} bytes): {src}"
                    )

                with src.open("rb") as fin, partial.open("wb") as fout:
                    shutil.copyfileobj(fin, fout, length=16 * 1024 * 1024)
                    fout.flush()
                    try:
                        os.fsync(fout.fileno())
                    except Exception:
                        pass

                after = src.stat()
                copied_size = partial.stat().st_size

                source_changed = (
                    int(before.st_size) != int(after.st_size)
                    or int(before.st_mtime_ns) != int(after.st_mtime_ns)
                    or int(copied_size) != int(after.st_size)
                )
                if source_changed:
                    last_error = RuntimeError(
                        "SeedVR2 source changed while it was being copied."
                    )
                    try:
                        partial.unlink(missing_ok=True)
                    except Exception:
                        pass
                    if attempt < 15:
                        self._post(
                            "log",
                            f"V162 SEEDVR2 PRESERVE RETRY {attempt}/15: "
                            "source changed during copy; waiting for a stable file."
                        )
                        time.sleep(0.5)
                        continue
                    break

                if dst.exists():
                    dst.unlink()
                os.replace(partial, dst)
                partial = None

            except Cancelled:
                raise
            except BackendError:
                raise
            except Exception as e:
                last_error = e
                if partial is not None:
                    try:
                        partial.unlink(missing_ok=True)
                    except Exception:
                        pass
                try:
                    temp_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass
                if attempt < 15:
                    self._post(
                        "log",
                        f"V162 SEEDVR2 PRESERVE RETRY {attempt}/15: "
                        f"destination={temp_dir}; error={e}"
                    )
                    time.sleep(0.5)
                    continue
                break

            try:
                preserved_info = self._probe_video(dst)
                self._validate_not_black_video(
                    dst,
                    f"verified SeedVR2 output for {job.info.path.name}"
                )

                expected_w, expected_h, ai_ref = self._seedvr2_expected_output_geometry(job, factor)

                if (
                    abs(preserved_info.width - expected_w) > 4
                    or abs(preserved_info.height - expected_h) > 4
                ):
                    raise BackendError(
                        f"Preserved SeedVR2 copy has wrong geometry: expected about "
                        f"{expected_w}x{expected_h}, got "
                        f"{preserved_info.width}x{preserved_info.height}: {dst}"
                    )

                complete, length_detail = self._seedvr2_full_length_check(preserved_info, ai_ref)
                if not complete:
                    raise BackendError(
                        f"Preserved SeedVR2 copy is incomplete: {length_detail}. "
                        "The output must contain essentially the entire AI input before "
                        f"it can be accepted: {dst}"
                    )

            except Cancelled:
                raise
            except BackendError:
                raise
            except Exception as e:
                raise BackendError(
                    f"SeedVR2 output was copied successfully but validation failed: "
                    f"{dst}. Validation error: {e}"
                ) from e

            self._post(
                "log",
                f"V162 SEEDVR2 OUTPUT PRESERVED AND VALIDATED: copied verified AI "
                f"result out of private ComfyUI runtime before cleanup: {src} -> {dst}"
            )
            return dst

        raise BackendError(
            f"Could not preserve the verified SeedVR2 output before ComfyUI "
            f"cleanup after 15 attempts: {src}. Last error: {last_error}"
        )

    def _resolved_ffprobe(self) -> Optional[str]:
        configured = str(self.ffprobe.get() or "").strip()
        candidates: List[Path] = []

        if configured:
            cp = Path(configured)
            if cp.is_file():
                return str(cp)
            found = shutil.which(configured)
            if found:
                return str(found)

        ffmpeg_raw = str(self.ffmpeg.get() or "").strip()
        if ffmpeg_raw:
            fp = Path(ffmpeg_raw)
            if fp.is_file():
                candidates.append(fp.with_name("ffprobe.exe" if os.name == "nt" else "ffprobe"))
            else:
                found_ffmpeg = shutil.which(ffmpeg_raw)
                if found_ffmpeg:
                    candidates.append(
                        Path(found_ffmpeg).with_name("ffprobe.exe" if os.name == "nt" else "ffprobe")
                    )

        root_raw = str(self.install_root.get() or "").strip()
        if root_raw:
            root = Path(root_raw)
            candidates.extend([
                root / "Tools" / "ffprobe.exe",
                root / "ffmpeg" / "bin" / "ffprobe.exe",
                root / "bin" / "ffprobe.exe",
            ])

        comfy_raw = str(self.comfy_root.get() or "").strip()
        if comfy_raw:
            comfy = Path(comfy_raw)
            candidates.extend([
                comfy / "Tools" / "ffprobe.exe",
                comfy.parent / "Tools" / "ffprobe.exe",
                comfy / "ffmpeg" / "bin" / "ffprobe.exe",
            ])

        for candidate in candidates:
            try:
                if candidate.is_file():
                    self.ffprobe.set(str(candidate))
                    return str(candidate)
            except Exception:
                pass
        return None

    def _probe_video_with_ffmpeg(self, path: Path) -> VideoInfo:
        ffmpeg = self._tool(self.ffmpeg.get())
        if not (Path(ffmpeg).is_file() or shutil.which(ffmpeg)):
            raise BackendError("Neither FFprobe nor FFmpeg could be found for reading video metadata.")

        cp = subprocess.run(
            [ffmpeg, "-hide_banner", "-i", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=self._no_window(),
        )
        raw = (cp.stderr or "") + "\n" + (cp.stdout or "")

        duration = 0.0
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", raw, re.I)
        if m:
            duration = int(m.group(1)) * 3600.0 + int(m.group(2)) * 60.0 + float(m.group(3))

        video_line = ""
        audio_line = ""
        for line in raw.splitlines():
            if not video_line and "Video:" in line:
                video_line = line
            if not audio_line and "Audio:" in line:
                audio_line = line

        width = height = 0
        fps = 0.0
        bitrate = 0
        vcodec = ""
        acodec = ""

        if video_line:
            m = re.search(r"Video:\s*([^,\s]+)", video_line)
            if m:
                vcodec = m.group(1)
            dims = re.findall(r"(?<!\d)(\d{2,5})x(\d{2,5})(?!\d)", video_line)
            if dims:
                width, height = map(int, dims[-1])
            m = re.search(r"(\d+(?:\.\d+)?)\s*fps\b", video_line, re.I)
            if m:
                fps = float(self._round_fps(float(m.group(1))))
            m = re.search(r"(\d+(?:\.\d+)?)\s*kb/s\b", video_line, re.I)
            if m:
                bitrate = int(round(float(m.group(1)) * 1000.0))

        if audio_line:
            m = re.search(r"Audio:\s*([^,\s]+)", audio_line)
            if m:
                acodec = m.group(1)

        frames = int(round(duration * fps)) if duration > 0 and fps > 0 else 0
        if width <= 0 or height <= 0:
            tail_lines = [ln.strip() for ln in raw.splitlines() if ln.strip()][-12:]
            detail = " | ".join(tail_lines)
            if len(detail) > 1400:
                detail = detail[-1400:]
            raise BackendError(
                "FFmpeg could not determine the video resolution."
                + (f" FFmpeg metadata tail: {detail}" if detail else "")
            )

        return VideoInfo(
            path=path,
            width=width,
            height=height,
            fps=fps,
            duration=duration,
            frames=frames,
            vcodec=vcodec,
            acodec=acodec,
            video_bitrate=bitrate,
            color_space="",
        )

    def _probe_video(self, path: Path) -> VideoInfo:
        ffprobe = self._resolved_ffprobe()
        if ffprobe:
            try:
                cmd = [
                    ffprobe, "-v", "error", "-print_format", "json",
                    "-show_streams", "-show_format", str(path)
                ]
                cp = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=self._no_window(),
                )
                if cp.returncode == 0:
                    data = json.loads(cp.stdout or "{}")
                    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
                    a = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})

                    width = self._to_int(v.get("width"))
                    height = self._to_int(v.get("height"))
                    if width > 0 and height > 0:
                        fps = 0.0
                        for rate_key in ("avg_frame_rate", "r_frame_rate"):
                            rate_raw = v.get(rate_key)
                            rate = float(self._round_fps(self._parse_rate(rate_raw or "0/1")))
                            if rate > 0:
                                fps = rate
                                break

                        dur = self._to_float(v.get("duration")) or self._to_float(
                            data.get("format", {}).get("duration")
                        )
                        frames = self._to_int(v.get("nb_frames")) or self._to_int(v.get("nb_read_frames"))

                        if fps <= 0 and frames and dur and dur > 0:
                            fps = float(self._round_fps(float(frames) / float(dur)))

                        if not frames and dur and fps > 0:
                            frames = int(round(dur * fps))

                        bitrate = self._to_int(v.get("bit_rate"))
                        return VideoInfo(
                            path=path,
                            width=width,
                            height=height,
                            fps=fps,
                            duration=dur,
                            frames=frames,
                            vcodec=str(v.get("codec_name") or ""),
                            acodec=str(a.get("codec_name") or ""),
                            video_bitrate=bitrate,
                            color_space=str(v.get("color_space") or ""),
                        )
                    self._post(
                        "log",
                        f"V137 FFprobe metadata warning for {path.name}: no usable video dimensions were returned; trying FFmpeg metadata fallback."
                    )
                else:
                    err = (cp.stderr or cp.stdout or "").strip().replace("\r", " ").replace("\n", " | ")
                    if len(err) > 1200:
                        err = err[-1200:]
                    self._post(
                        "log",
                        f"V137 FFprobe metadata warning for {path.name}: return code {cp.returncode}"
                        + (f"; {err}" if err else "")
                        + "; trying FFmpeg metadata fallback."
                    )
            except Exception as e:
                self._post("log", f"FFprobe warning for {path.name}: {e}; trying FFmpeg metadata fallback.")

        return self._probe_video_with_ffmpeg(path)

    @staticmethod
    def _same_video_path(a: Path, b: Path) -> bool:
        try:
            return os.path.normcase(os.path.abspath(str(a))) == os.path.normcase(os.path.abspath(str(b)))
        except Exception:
            return str(a) == str(b)

    def _probe_video_resilient(
        self,
        path: Path,
        fallback: Optional[VideoInfo] = None,
        context: str = "video",
    ) -> VideoInfo:
        path = Path(path)
        try:
            return self._probe_video(path)
        except Exception as e:
            if (
                fallback is not None
                and int(fallback.width or 0) > 0
                and int(fallback.height or 0) > 0
                and self._same_video_path(path, Path(fallback.path))
            ):
                self._post(
                    "log",
                    f"V137 METADATA FALLBACK: fresh probe failed for {context} '{path.name}': {e}. "
                    f"Using already-validated queue metadata "
                    f"{fallback.width}x{fallback.height} @ {self._fmt_fps(float(fallback.fps or 0.0))} FPS."
                )
                return VideoInfo(
                    path=path,
                    width=int(fallback.width or 0),
                    height=int(fallback.height or 0),
                    fps=float(fallback.fps or 0.0),
                    duration=float(fallback.duration or 0.0),
                    frames=int(fallback.frames or 0),
                    vcodec=str(fallback.vcodec or ""),
                    acodec=str(fallback.acodec or ""),
                    video_bitrate=int(fallback.video_bitrate or 0),
                    color_space=str(fallback.color_space or ""),
                )
            raise

    @staticmethod
    def _timestamp_sensitive_container(path: Path) -> bool:
        return path.suffix.lower() in {".mpg", ".mpeg", ".vob", ".ts", ".m2ts", ".mts", ".m2v"}

    def _pre_ai_encode_args(self, info: VideoInfo, cq: int = TEMP_NVENC_CQ) -> Tuple[List[str], str]:
        width = int(info.width or 0)
        height = int(info.height or 0)

        if width > 0 and height > 0 and (width < 256 or height < 256):
            return [
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "0",
                "-pix_fmt", "yuv420p",
            ], "CPU libx264 lossless fallback for small-frame video (CRF 0)"

        return [
            "-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq",
            "-rc", "vbr", "-cq", str(cq), "-b:v", "0",
            "-multipass", "fullres", "-profile:v", "high",
            "-pix_fmt", "yuv420p",
        ], f"NVIDIA NVENC H.264 very high quality (CQ {cq}, p7)"

    def _repair_auto(self, job: Job, repaired_dir: Path) -> Path:
        src = job.info.path
        legacy_mpeg = self._timestamp_sensitive_container(src)


        self._post("log", f"Checking source integrity and A/V timeline: {src}")
        check_cmd = [
            self._tool(self.ffmpeg.get()), "-hide_banner", "-v", "error", "-stats_period", "1",
            "-err_detect", "explode", "-i", str(src),
            "-map", "0:v:0", "-map", "0:a?", "-f", "null", "-"
        ]
        rc, lines = self._run_collect(
            check_cmd, job=job, duration=job.info.duration,
            progress_callback=lambda f: self._set_stage_fraction(job, min(0.70, f * 0.70))
        )
        errors = [x for x in lines if self._looks_like_media_error(x)]


        if rc == 0 and not errors and not legacy_mpeg:
            self._post("log", "Source decode/timeline check: clean; no repair file needed.")
            return src

        if legacy_mpeg:
            self._post("log", "Legacy MPEG container detected: rebuilding A/V timestamps to prevent audio/video drift.")
        else:
            self._post("log", "Source corruption/container problem detected. Trying lossless stream remux with regenerated timestamps...")


        if not legacy_mpeg:
            remux = repaired_dir / f"{self._safe_stem(src.stem)}_REPAIRED_REMUX.mkv"
            cmd = [
                self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "warning",
                "-fflags", "+genpts+discardcorrupt", "-err_detect", "ignore_err", "-i", str(src),
                "-map", "0", "-c", "copy", "-avoid_negative_ts", "make_zero", "-max_interleave_delta", "0",
                "-progress", "pipe:1", "-nostats", str(remux)
            ]
            rc = self._run_process(
                cmd, job, duration=job.info.duration, ffmpeg_progress=True,
                progress_callback=lambda f: self._set_stage_fraction(job, 0.70 + f * 0.15)
            )
            if rc == 0 and remux.exists() and remux.stat().st_size > 1024:
                try:
                    remux_info = self._probe_video(remux)
                    cmdv = [
                        self._tool(self.ffmpeg.get()), "-hide_banner", "-v", "error", "-err_detect", "explode",
                        "-i", str(remux), "-map", "0:v:0", "-map", "0:a?", "-f", "null", "-"
                    ]
                    rc2, lines2 = self._run_collect(cmdv, job=job, duration=remux_info.duration)
                    if rc2 == 0 and not any(self._looks_like_media_error(x) for x in lines2):
                        self._post("log", f"Repair succeeded by remux: {remux}")
                        return remux
                except Exception:
                    pass


        repair_encode_args, repair_encoder = self._pre_ai_encode_args(job.info, TEMP_NVENC_CQ)
        if "libx264" in repair_encode_args:
            self._post(
                "log",
                f"V137 SMALL-FRAME ENCODER FALLBACK: source={job.info.width}x{job.info.height}; "
                "using lossless CPU libx264 for the repair intermediate because NVENC does not support this small frame size reliably."
            )
        self._post("log", f"Rebuilding synchronized video/audio timeline with {repair_encoder} + AAC...")
        rebuilt = repaired_dir / f"{self._safe_stem(src.stem)}_REPAIRED_SYNC.mkv"
        cmd = [
            self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "warning",
            "-fflags", "+genpts+discardcorrupt", "-err_detect", "ignore_err", "-i", str(src),
            "-map", "0:v:0", "-map", "0:a?", "-map", "0:s?",
            "-vf", "setpts=PTS-STARTPTS",
        ] + repair_encode_args
        if job.info.fps and job.info.fps > 1:
            cmd += ["-r", f"{job.info.fps:.6f}", "-fps_mode:v", "cfr"]
        if job.info.acodec:
            cmd += [
                "-af", "aresample=async=1000:first_pts=0",
                "-c:a", "aac", "-b:a", "192k"
            ]
        cmd += [
            "-c:s", "copy", "-avoid_negative_ts", "make_zero", "-max_interleave_delta", "0",
            "-progress", "pipe:1", "-nostats", str(rebuilt)
        ]
        rc = self._run_process(
            cmd, job, duration=job.info.duration, ffmpeg_progress=True,
            progress_callback=lambda f: self._set_stage_fraction(job, 0.85 + f * 0.15)
        )
        if rc != 0 or not rebuilt.exists() or rebuilt.stat().st_size < 1024:
            raise BackendError("Automatic video repair / A-V synchronization failed.")
        self._post("log", f"Repair succeeded with normalized A/V timestamps: {rebuilt}")
        return rebuilt

    def _preprocess_fps_reduce(
        self,
        job: Job,
        source: Path,
        temp_dir: Path,
    ) -> Tuple[Path, VideoInfo]:
        source_info = self._probe_video(source)
        target_fps, mode, value, applied = self._fps_reduction_plan(job.info)
        if not applied or source_info.fps <= 0:
            self._post(
                "log",
                f"FPS Reduce: Off/no reduction - AI receives {source_info.fps:.6g} FPS."
            )
            return source, source_info


        target_fps = min(float(target_fps), float(source_info.fps))
        if target_fps >= source_info.fps - 0.01:
            return source, source_info

        output = temp_dir / "fps_reduced_pre_ai.mkv"
        fps_encode_args, fps_encoder = self._pre_ai_encode_args(source_info, TEMP_NVENC_CQ)
        cmd = [
            self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "warning",
            "-i", str(source),
            "-map", "0:v:0", "-map", "0:a?",
            "-vf", f"fps=fps={self._round_fps(target_fps)}:round=near",
        ] + fps_encode_args + [
            "-c:a", "copy",
            "-fps_mode:v", "cfr",
            "-progress", "pipe:1", "-nostats", str(output),
        ]
        self._post(
            "log",
            f"FPS Reduce: {self._fmt_fps(source_info.fps)} → {self._fmt_fps(target_fps)} FPS; mode={mode}; setting={value:g}; encoder={fps_encoder}."
        )
        rc = self._run_process(
            cmd,
            job,
            duration=job.info.duration,
            ffmpeg_progress=True,
            progress_callback=lambda f: self._set_stage_fraction(job, f),
        )
        if rc != 0 or not output.is_file():
            raise BackendError("FPS reduction FFmpeg step failed.")
        out_info = self._probe_video(output)
        if out_info.duration > 0 and job.info.duration > 0 and out_info.duration < job.info.duration * 0.90:
            raise BackendError(
                f"FPS reduction produced a video that is too short: {out_info.duration:.3f}s vs source {job.info.duration:.3f}s."
            )
        self._post(
            "log",
            f"FPS Reduce complete: AI input={out_info.width}x{out_info.height} @ {self._fmt_fps(out_info.fps)} FPS, "
            f"frames={out_info.frames or '?'}; duration={out_info.duration:.3f}s."
        )
        return output, out_info

    def _auto_denoise_filter(self, src: Path, info: VideoInfo) -> Tuple[str, str]:
        duration = max(0.0, float(info.duration or 0.0))
        if duration > 2.0:
            fractions = (0.05, 0.17, 0.31, 0.50, 0.69, 0.83, 0.95)
            sample_times = [duration * x for x in fractions]
        else:
            sample_times = [0.0]

        residuals: List[float] = []
        sampled_frames = 0

        for sample_time in sample_times:
            self._wait_if_paused()
            if self.stop_event.is_set():
                raise Cancelled()

            pixels = self._sample_rgb_pixels(src, sample_time)
            if len(pixels) < 160 * 4:
                continue

            height = len(pixels) // 160
            usable = pixels[:160 * height]
            if height < 4:
                continue

            luma = [
                0.2126 * r + 0.7152 * g + 0.0722 * b
                for r, g, b in usable
            ]
            frame_residuals: List[float] = []

            for y in range(1, height - 1):
                row = y * 160
                for x in range(1, 159):
                    idx = row + x
                    c = luma[idx]
                    if c < 20.0 or c > 235.0:
                        continue
                    neighbors = (
                        luma[idx - 1],
                        luma[idx + 1],
                        luma[idx - 160],
                        luma[idx + 160],
                    )
                    if max(neighbors) - min(neighbors) > 14.0:
                        continue
                    smooth = sum(neighbors) / 4.0
                    frame_residuals.append(abs(c - smooth))

            if frame_residuals:
                frame_residuals.sort()
                keep = frame_residuals[:max(40, int(len(frame_residuals) * 0.80))]
                residuals.extend(keep)
                sampled_frames += 1

        noise50 = self._percentile_value(residuals, 0.50)
        noise80 = self._percentile_value(residuals, 0.80)

        bppf = 0.0
        if info.video_bitrate and info.width and info.height and info.fps:
            bppf = float(info.video_bitrate) / max(
                1.0,
                float(info.width) * float(info.height) * float(info.fps),
            )

        score = 0.0
        if noise50 is not None:
            score += max(0.0, noise50 - 0.8) * 0.65
        if noise80 is not None:
            score += max(0.0, noise80 - 1.5) * 0.35
        if bppf > 0:
            if bppf < 0.025:
                score += 1.8
            elif bppf < 0.045:
                score += 1.1
            elif bppf < 0.075:
                score += 0.5

        if score < 0.85:
            strength = 0.0
        elif score < 1.8:
            strength = 0.85
        elif score < 3.0:
            strength = 1.35
        elif score < 4.5:
            strength = 2.00
        else:
            strength = 2.80

        if strength <= 0:
            filt = ""
        else:
            chroma = max(0.70, strength * 0.90)
            temporal = max(1.20, strength * 1.90)
            temporal_chroma = max(1.00, chroma * 1.80)
            filt = (
                f"hqdn3d={strength:.3f}:{chroma:.3f}:"
                f"{temporal:.3f}:{temporal_chroma:.3f}"
            )

        stats = (
            f"frames={sampled_frames}; "
            f"noise50={noise50:.3f}" if noise50 is not None
            else f"frames={sampled_frames}; noise50=NA"
        )
        stats += f"; noise80={noise80:.3f}" if noise80 is not None else "; noise80=NA"
        stats += f"; bppf={bppf:.5f}; score={score:.3f}; strength={strength:.2f}"

        return filt, stats

    def _preprocess_denoise(self, job: Job, src: Path, temp_dir: Path) -> Path:
        if not self._enhancement_is_enabled() or self._job_setting("denoise", self.denoise) != "Auto":
            self._post("log", "Denoise skipped (Enhancement OFF or Denoise Off).")
            return src

        src_info = self._probe_video(src)
        filt, stats = self._auto_denoise_filter(src, src_info)

        if not filt:
            self._post(
                "log",
                f"V62 AUTO DENOISE: {stats}; no denoise was required."
            )
            return src

        self._post(
            "log",
            f"V62 AUTO DENOISE: {stats}; filter={filt}"
        )

        out = temp_dir / "denoised_pre_ai.mkv"
        denoise_encode_args, denoise_encoder = self._pre_ai_encode_args(src_info, TEMP_NVENC_CQ)
        self._post("log", f"Denoise preprocessing encoder: {denoise_encoder}.")
        cmd = [
            self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "warning", "-i", str(src),
            "-map", "0:v:0", "-map", "0:a?", "-vf", filt,
        ] + denoise_encode_args + [
            "-c:a", "copy", "-progress", "pipe:1", "-nostats", str(out)
        ]
        rc = self._run_process(
            cmd,
            job,
            duration=job.info.duration,
            ffmpeg_progress=True,
            progress_callback=lambda f: self._set_stage_fraction(job, f),
        )
        if rc != 0:
            raise BackendError("Automatic denoise preprocessing failed.")
        return out


    @staticmethod
    def _idet_counts(lines: List[str]) -> Dict[str, Dict[str, int]]:
        """Parse FFmpeg idet's final single-frame and multi-frame classifications."""
        parsed: Dict[str, Dict[str, int]] = {}
        pattern = re.compile(
            r"(Single|Multi) frame detection:\s*"
            r"TFF:\s*(\d+)\s+BFF:\s*(\d+)\s+"
            r"Progressive:\s*(\d+)\s+Undetermined:\s*(\d+)", re.I
        )
        for line in lines:
            match = pattern.search(line)
            if not match:
                continue
            label = match.group(1).lower()
            parsed[label] = dict(zip(
                ("tff", "bff", "progressive", "undetermined"),
                (int(match.group(i)) for i in range(2, 6)),
            ))
        return parsed

    def _source_field_order(self, source: Path) -> str:
        """Read field order without trusting container flags as proof of interlacing."""
        ffprobe = self._resolved_ffprobe()
        if not ffprobe:
            return "unknown"
        try:
            cp = subprocess.run(
                [
                    ffprobe, "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=field_order", "-of",
                    "default=noprint_wrappers=1:nokey=1", str(source),
                ],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace",
                timeout=25, creationflags=self._no_window(),
            )
            if cp.returncode == 0:
                return str(cp.stdout or "").strip().splitlines()[0].strip().lower() if str(cp.stdout or "").strip() else "unknown"
        except (OSError, subprocess.TimeoutExpired):
            pass
        return "unknown"

    def _combing_pixel_evidence(self, job: Job, source: Path, info: VideoInfo) -> Tuple[bool, str]:
        """Validate idet using actual alternate-line spatial inconsistency.

        Vertical resolution is *not* downscaled: doing that would hide the
        single-scanline combing we are trying to recognize. Samples are reduced
        in width only; processing needs no third-party Python libraries.
        """
        height = min(720, (max(0, int(info.height)) // 2) * 2)
        width = min(160, (max(0, int(info.width)) // 2) * 2)
        if height < 32 or width < 32:
            return False, "image too small for reliable alternate-line analysis"
        top = max(0, ((int(info.height) - height) // 4) * 2)
        frame_bytes = width * height
        duration = max(0.0, float(info.duration or 0.0))
        if duration <= 6.0 or duration <= 0.0:
            positions = [0.0]
        else:
            positions = [max(0.0, duration * fraction - 0.35) for fraction in (0.12, 0.50, 0.88)]
        block_scores: List[float] = []
        numerator_total = 0.0
        denominator_total = 0.0
        frames_checked = 0
        hot_blocks = 0
        for start in positions:
            self._wait_if_paused()
            if self.stop_event.is_set():
                raise Cancelled()
            cmd = [
                self._tool(self.ffmpeg.get()), "-hide_banner", "-loglevel", "error",
                "-ss", f"{start:.4f}", "-i", str(source),
                "-map", "0:v:0", "-an", "-sn", "-dn",
                "-vf", f"crop=iw:{height}:0:{top},scale={width}:{height}:flags=area,format=gray",
                "-frames:v", "6", "-f", "rawvideo", "pipe:1",
            ]
            try:
                cp = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    timeout=45, creationflags=self._no_window(),
                )
            except (OSError, subprocess.TimeoutExpired) as e:
                self._post("log", f"V220 COMB PIXEL CHECK: FFmpeg sampling error: {e}")
                continue
            if cp.returncode != 0 or not cp.stdout:
                self._post("log", f"V220 COMB PIXEL CHECK: FFmpeg pixel sampling failed (rc={cp.returncode}).")
                continue
            raw = cp.stdout
            count = len(raw) // frame_bytes
            for frame_index in range(min(6, count)):
                self._wait_if_paused()
                if self.stop_event.is_set():
                    raise Cancelled()
                frame = memoryview(raw)[frame_index * frame_bytes:(frame_index + 1) * frame_bytes]
                frames_checked += 1
                # 16x12 odd-line spatial blocks, every second horizontal pixel.
                for odd_y in range(1, height - 1, 24):
                    for left_x in range(0, width - 8, 16):
                        residual = 0
                        spatial = 0
                        n = 0
                        for y in range(odd_y, min(odd_y + 24, height - 1), 2):
                            off_top = (y - 1) * width
                            off_odd = y * width
                            off_bottom = (y + 1) * width
                            for x in range(left_x, min(left_x + 16, width), 2):
                                top_v = frame[off_top + x]
                                odd_v = frame[off_odd + x]
                                bot_v = frame[off_bottom + x]
                                residual += abs(2 * odd_v - top_v - bot_v)
                                spatial += abs(top_v - bot_v)
                                n += 1
                        if n == 0 or spatial < n * 0.9:
                            continue
                        # |odd - mean(even neighbors)| / |even above - even below|
                        ratio = residual / (2.0 * spatial)
                        block_scores.append(ratio)
                        numerator_total += residual
                        denominator_total += 2.0 * spatial
                        if ratio >= 1.0:
                            hot_blocks += 1
        if frames_checked == 0 or len(block_scores) < 12:
            return False, f"insufficient frames/texture ({frames_checked} frames, {len(block_scores)} blocks)"
        block_scores.sort()
        def percentile(p: float) -> float:
            return block_scores[min(len(block_scores) - 1, int(p * (len(block_scores) - 1)))]
        global_ratio = numerator_total / max(1, denominator_total)
        p95 = percentile(.95)
        p99 = percentile(.99)
        confirmed = (
            global_ratio >= 0.78 or p95 >= 0.84
            or (p99 >= 1.00 and p95 >= 0.72 and hot_blocks >= 3)
        )
        return confirmed, (
            f"{frames_checked} frames; {len(block_scores)} textured blocks; "
            f"combing global={global_ratio:.3f}, p95={p95:.3f}, "
            f"p99={p99:.3f}, strong blocks={hot_blocks}; "
            f"{'CONFIRMED' if confirmed else 'NOT CONFIRMED'}"
        )

    def _auto_deinterlace_filter(self, job: Job, source: Path, info: VideoInfo) -> str:
        """Conservatively auto-detect source combing and return BWDIF or no filter.

        FFmpeg idet inspects decoded picture content, not just codec field-order flags.
        send_frame retains the existing FPS; all is required for baked-in combing
        in sources tagged progressive. Runs before any AI or frame-size changes.
        """
        job.deinterlace_applied = False
        job.deinterlace_diagnostic = ""
        if not self._enhancement_is_enabled() or not bool(self._job_setting("deinterlace_auto", self.deinterlace_auto)):
            self._post("log", "V261 DEINTERLACE AUTO: skipped (Enhancement OFF or Deinterlace No).")
            return ""

        self._wait_if_paused()
        if self.stop_event.is_set():
            raise Cancelled()

        # Prefer original metadata: a prior source-repair encode can erase field flags.
        original_field = self._source_field_order(job.info.path)
        working_field = self._source_field_order(source) if source != job.info.path else original_field
        source_interlaced = original_field in {"tt", "bb", "tb", "bt"}
        working_interlaced = working_field in {"tt", "bb", "tb", "bt"}
        duration = max(0.0, float(info.duration or 0.0))
        fps = max(1.0, float(info.fps or 25.0))

        if 0.0 < duration <= 6.0:
            windows = [(0.0, min(3.0, duration))]
        elif duration > 6.0:
            window_length = 2.5
            windows = [
                (max(0.0, min(duration - window_length, duration * part - window_length / 2.0)), window_length)
                for part in (0.12, 0.50, 0.88)
            ]
        else:
            windows = [(0.0, 2.5)]

        totals: Dict[str, Dict[str, int]] = {
            "single": {k: 0 for k in ("tff", "bff", "progressive", "undetermined")},
            "multi": {k: 0 for k in ("tff", "bff", "progressive", "undetermined")},
        }
        samples_ok = 0
        for start, seconds in windows:
            self._wait_if_paused()
            if self.stop_event.is_set():
                raise Cancelled()
            max_frames = max(8, int(round(seconds * fps)))
            cmd = [
                self._tool(self.ffmpeg.get()), "-hide_banner", "-loglevel", "info",
                "-ss", f"{start:.4f}", "-i", str(source),
                "-map", "0:v:0", "-an", "-sn", "-dn",
                "-vf", "idet", "-frames:v", str(max_frames),
                "-f", "null", "-",
            ]
            rc, lines = self._run_collect(cmd, job=job)
            counts = self._idet_counts(lines)
            if rc != 0 or "multi" not in counts:
                self._post("log", f"V220 DEINTERLACE AUTO: idet sample at {start:.2f}s unavailable (rc={rc}).")
                continue
            samples_ok += 1
            for mode, values in counts.items():
                if mode in totals:
                    for key in totals[mode]:
                        totals[mode][key] += int(values.get(key, 0))

        m = totals["multi"]
        s = totals["single"]
        multi_inter = m["tff"] + m["bff"]
        multi_classified = multi_inter + m["progressive"]
        single_inter = s["tff"] + s["bff"]
        single_classified = single_inter + s["progressive"]
        multi_fraction = multi_inter / max(1, multi_classified)
        single_fraction = single_inter / max(1, single_classified)

        # Multi-frame idet is more selective than single-frame idet; requiring
        # corroboration limits deinterlacing false positives in detailed/noisy video.
        pixel_interlaced = (
            multi_inter >= 5 and multi_fraction >= 0.08
            and (single_inter >= 5 or multi_fraction >= 0.20)
        )
        # idet alone can confidently mislabel progressive material as interlaced
        # (for example, fast-moving synthetic graphics). Require independent
        # alternate-line evidence unless the stream explicitly declares fields.
        spatial_confirmed = False
        spatial_message = "not required (no idet evidence)"
        if pixel_interlaced and not (source_interlaced or working_interlaced):
            spatial_confirmed, spatial_message = self._combing_pixel_evidence(job, source, info)
        detected = source_interlaced or working_interlaced or (pixel_interlaced and spatial_confirmed)
        diagnostic = (
            f"samples={samples_ok}/{len(windows)}; field_order(original={original_field}, "
            f"working={working_field}); idet multi TFF={m['tff']} BFF={m['bff']} "
            f"P={m['progressive']} U={m['undetermined']} ({multi_fraction:.1%} interlaced); "
            f"single TFF={s['tff']} BFF={s['bff']} P={s['progressive']} "
            f"U={s['undetermined']} ({single_fraction:.1%} interlaced)"
        )
        diagnostic += f"; pixel validation: {spatial_message}"
        job.deinterlace_diagnostic = diagnostic
        self._post("log", f"V220 DEINTERLACE AUTO SCAN: {diagnostic}")
        if not detected:
            self._post(
                "log",
                "V220 DEINTERLACE AUTO: no sufficiently convincing interlacing detected; "
                "progressive video retained unchanged. Auto detection may miss mild or "
                "previously resized/baked-in combing.",
            )
            return ""

        # For an already-combed progressive stream, 'deint=all' is essential.
        if m["tff"] >= m["bff"] * 1.5 and m["tff"] >= 3:
            parity = "tff"
        elif m["bff"] >= m["tff"] * 1.5 and m["bff"] >= 3:
            parity = "bff"
        elif original_field in {"tt", "tb"} or working_field in {"tt", "tb"}:
            parity = "tff"
        elif original_field in {"bb", "bt"} or working_field in {"bb", "bt"}:
            parity = "bff"
        else:
            parity = "auto"
        vf = f"bwdif=mode=send_frame:parity={parity}:deint=all"
        job.deinterlace_applied = True
        self._post(
            "log",
            f"V220 DEINTERLACE AUTO: interlacing detected; APPLY {vf} "
            "as FIRST pre-AI video filter. Frame rate unchanged.",
        )
        return vf

    def _preprocess_pre_ai_fused(
        self,
        job: Job,
        source: Path,
        temp_dir: Path,
    ) -> Tuple[Path, VideoInfo, bool, bool]:
        source_info = self._probe_video(source)
        filters: List[str] = []
        fps_applied = False
        denoise_applied = False

        deinterlace_filter = self._auto_deinterlace_filter(job, source, source_info)
        if deinterlace_filter:
            filters.append(deinterlace_filter)

        target_fps, mode, value, applied = self._fps_reduction_plan(job.info)
        if not applied or source_info.fps <= 0:
            self._post(
                "log",
                f"FPS Reduce: Off/no reduction - AI receives {source_info.fps:.6g} FPS."
            )
        else:
            target_fps = min(float(target_fps), float(source_info.fps))
            if target_fps < source_info.fps - 0.01:
                filters.append(f"fps=fps={self._round_fps(target_fps)}:round=near")
                fps_applied = True
                self._post(
                    "log",
                    f"FPS Reduce: {self._fmt_fps(source_info.fps)} → {self._fmt_fps(target_fps)} FPS; mode={mode}; setting={value:g}."
                )
            else:
                self._post(
                    "log",
                    f"FPS Reduce: Off/no reduction - AI receives {source_info.fps:.6g} FPS."
                )

        if not self._enhancement_is_enabled() or self._job_setting("denoise", self.denoise) != "Auto":
            self._post("log", "Denoise skipped (Enhancement OFF or Denoise Off).")
        else:
            denoise_filter, denoise_stats = self._auto_denoise_filter(source, source_info)
            if denoise_filter:
                filters.append(denoise_filter)
                denoise_applied = True
                self._post(
                    "log",
                    f"V137 AUTO DENOISE: {denoise_stats}; filter={denoise_filter}"
                )
            else:
                self._post(
                    "log",
                    f"V137 AUTO DENOISE: {denoise_stats}; no denoise was required."
                )

        if self._selected_downscale_enable() and self._selected_upscale_enable():
            target_w, target_h = self._downscale_dimensions(source_info.width, source_info.height)
            if (target_w, target_h) != (source_info.width, source_info.height):
                filters.append(f"scale={target_w}:{target_h}:flags=lanczos")
                self._post(
                    "log", f"V216 LANCZOS PRE-AI DOWNSCALE: "
                    f"{source_info.width}x{source_info.height} -> {target_w}x{target_h}; "
                    f"factor={self._selected_downscale_factor():g}X; upscale remains {'ON' if self._selected_upscale_enable() else 'OFF'}."
                )

        if not filters:
            self._post(
                "log",
                "V220 LOW-LOSS PRE-AI: no deinterlacing, FPS reduction, denoise, or downscale needed; source video preserved."
            )
            return source, source_info, fps_applied, denoise_applied

        out = temp_dir / "pre_ai_fused.mkv"
        encoder_info = copy.copy(source_info)
        if self._selected_downscale_enable() and self._selected_upscale_enable():
            encoder_info.width, encoder_info.height = self._downscale_dimensions(source_info.width, source_info.height)
        fused_encode_args, fused_encoder = self._pre_ai_encode_args(encoder_info, TEMP_NVENC_CQ)
        if "libx264" in fused_encode_args:
            self._post(
                "log",
                f"V137 SMALL-FRAME ENCODER FALLBACK: source={source_info.width}x{source_info.height}; "
                "NVENC cannot encode this frame size reliably, so the pre-AI intermediate will use lossless CPU libx264."
            )
        vf = ",".join(filters)
        self._post(
            "log",
            f"V220 LOW-LOSS PRE-AI: combining deinterlacing/FPS reduction/denoise/downscale into one FFmpeg pass to limit generational compression loss; encoder={fused_encoder}; filter={vf}"
        )
        cmd = [
            self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "warning",
            "-i", str(source),
            "-map", "0:v:0", "-map", "0:a?", "-vf", vf,
        ] + fused_encode_args + [
            "-c:a", "copy",
            "-fps_mode:v", "cfr",
            "-progress", "pipe:1", "-nostats", str(out),
        ]
        rc = self._run_process(
            cmd,
            job,
            duration=job.info.duration,
            ffmpeg_progress=True,
            progress_callback=lambda f: self._set_stage_fraction(job, f),
        )
        if rc != 0 or not out.is_file():
            raise BackendError("V220 fused pre-AI deinterlacing / FPS reduction / denoise / downscale processing failed. Check the FFmpeg command and logs.")
        out_info = self._probe_video(out)
        if fps_applied and out_info.duration > 0 and job.info.duration > 0 and out_info.duration < job.info.duration * 0.90:
            raise BackendError(
                f"Fused preprocessing produced a video that is too short: {out_info.duration:.3f}s vs source {job.info.duration:.3f}s."
            )
        self._post(
            "log",
            f"V176 LOW-LOSS PRE-AI complete: AI input={out_info.width}x{out_info.height} @ {self._fmt_fps(out_info.fps)} FPS, frames={out_info.frames or '?'}; duration={out_info.duration:.3f}s."
        )
        return out, out_info, fps_applied, denoise_applied

    @staticmethod
    def _median_value(values: List[float]) -> Optional[float]:
        vals = sorted(float(x) for x in values if math.isfinite(float(x)))
        if not vals:
            return None
        n = len(vals)
        mid = n // 2
        if n % 2:
            return vals[mid]
        return (vals[mid - 1] + vals[mid]) / 2.0

    @staticmethod
    def _percentile_value(values: List[float], fraction: float) -> Optional[float]:
        vals = sorted(float(x) for x in values if math.isfinite(float(x)))
        if not vals:
            return None
        if len(vals) == 1:
            return vals[0]
        fraction = min(1.0, max(0.0, float(fraction)))
        pos = fraction * (len(vals) - 1)
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            return vals[lo]
        part = pos - lo
        return vals[lo] * (1.0 - part) + vals[hi] * part

    def _sample_rgb_pixels(self, src: Path, sample_time: float) -> List[Tuple[int, int, int]]:
        cmd = [
            self._tool(self.ffmpeg.get()),
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{max(0.0, float(sample_time)):.3f}",
            "-i",
            str(src),
            "-frames:v",
            "1",
            "-an",
            "-sn",
            "-vf",
            "scale=160:-2:flags=area,format=rgb24",
            "-f",
            "rawvideo",
            "pipe:1",
        ]
        cp = subprocess.run(
            cmd,
            capture_output=True,
            text=False,
            timeout=45,
            creationflags=self._no_window(),
        )
        if cp.returncode != 0 or not cp.stdout:
            return []
        raw = cp.stdout
        usable = len(raw) - (len(raw) % 3)
        return [
            (raw[i], raw[i + 1], raw[i + 2])
            for i in range(0, usable, 3)
        ]

    def _static_auto_correction_filter(self, src: Path, info: VideoInfo, color: str, brightness: str, white: str) -> Tuple[str, str]:
        if "Auto" not in {color, brightness, white}:
            return "", ""

        duration = max(0.0, float(info.duration or 0.0))
        if duration > 2.0:
            fractions = (0.05, 0.17, 0.31, 0.50, 0.69, 0.83, 0.95)
            sample_times = [duration * x for x in fractions]
        else:
            sample_times = [0.0]

        all_luma: List[float] = []
        all_sat: List[float] = []
        neutral: List[Tuple[float, int, int, int]] = []
        wb_pixels: List[Tuple[float, float, int, int, int]] = []
        sampled_frames = 0

        for sample_time in sample_times:
            self._wait_if_paused()
            if self.stop_event.is_set():
                raise Cancelled()

            pixels = self._sample_rgb_pixels(src, sample_time)
            if not pixels:
                continue

            sampled_frames += 1

            for r, g, b in pixels:
                mx = max(r, g, b)
                mn = min(r, g, b)
                luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
                chroma = float(mx - mn)
                sat = chroma / max(1.0, float(mx))

                if 20.0 <= luma <= 245.0:
                    all_luma.append(luma)
                    all_sat.append(sat)
                    if 32.0 <= luma <= 242.0:
                        wb_pixels.append((luma, sat, r, g, b))

                if 48.0 <= luma <= 238.0 and sat <= 0.24:
                    score = sat + abs(luma - 150.0) / 3000.0
                    neutral.append((score, r, g, b))

        filters = []

        wb_text = "WB=not requested"
        if white == "Auto":
            strict_result = None
            if neutral:
                neutral.sort(key=lambda x: x[0])
                take = min(len(neutral), max(300, int(len(neutral) * 0.18)))
                selected = neutral[:take]
                nr = self._median_value([x[1] for x in selected])
                ng = self._median_value([x[2] for x in selected])
                nb = self._median_value([x[3] for x in selected])
                if nr and ng and nb:
                    strict_result = (float(nr), float(ng), float(nb), len(selected), len(neutral))

            broad_result = None
            if wb_pixels:
                lumas = [x[0] for x in wb_pixels]
                bright_cut = self._percentile_value(lumas, 0.72)
                if bright_cut is None:
                    bright_cut = 150.0
                candidates = [x for x in wb_pixels if x[0] >= bright_cut and x[1] <= 0.52]
                if len(candidates) < 120:
                    candidates = [x for x in wb_pixels if x[0] >= bright_cut and x[1] <= 0.68]
                if candidates:
                    candidates.sort(key=lambda x: (x[1] * 1.55) - (x[0] / 1020.0))
                    broad_take = min(len(candidates), max(120, int(len(candidates) * 0.22)))
                    broad = candidates[:broad_take]
                    br = self._median_value([x[2] for x in broad])
                    bg = self._median_value([x[3] for x in broad])
                    bb = self._median_value([x[4] for x in broad])
                    if br and bg and bb:
                        broad_result = (float(br), float(bg), float(bb), len(broad), len(candidates))

            global_result = None
            if wb_pixels:
                gr = self._median_value([x[2] for x in wb_pixels])
                gg = self._median_value([x[3] for x in wb_pixels])
                gb = self._median_value([x[4] for x in wb_pixels])
                if gr and gg and gb:
                    global_result = (float(gr), float(gg), float(gb))

            method = "none"
            source_rgb = None
            source_counts = ""

            if strict_result is not None:
                nr, ng, nb, nsel, ntotal = strict_result
                strict_mean = (nr + ng + nb) / 3.0
                strict_cast = max(abs(nr / strict_mean - 1.0), abs(ng / strict_mean - 1.0), abs(nb / strict_mean - 1.0))
                neutral_fraction = ntotal / max(1.0, float(len(wb_pixels)))
                if neutral_fraction >= 0.010 or strict_cast <= 0.10:
                    method = "neutral-reference"
                    source_rgb = (nr, ng, nb)
                    source_counts = f"neutral={nsel}/{ntotal}"

            if source_rgb is None and broad_result is not None:
                br, bg, bb, bsel, btotal = broad_result
                method = "bright-reference fallback"
                source_rgb = (br, bg, bb)
                source_counts = f"bright={bsel}/{btotal}"

            if source_rgb is None and global_result is not None:
                method = "global-cast fallback"
                source_rgb = global_result
                source_counts = f"pixels={len(wb_pixels)}"

            if source_rgb is not None:
                nr, ng, nb = source_rgb
                target = (nr + ng + nb) / 3.0
                raw_r = target / max(1e-6, nr)
                raw_g = target / max(1e-6, ng)
                raw_b = target / max(1e-6, nb)

                cast_strength = max(abs(raw_r - 1.0), abs(raw_g - 1.0), abs(raw_b - 1.0))
                if method == "neutral-reference":
                    blend = 0.30 if cast_strength < 0.18 else 0.42
                elif method == "bright-reference fallback":
                    blend = 0.24 if cast_strength < 0.16 else 0.34
                else:
                    blend = 0.18 if cast_strength < 0.16 else 0.26

                r_gain = 1.0 + (raw_r - 1.0) * blend
                g_gain = 1.0 + (raw_g - 1.0) * blend
                b_gain = 1.0 + (raw_b - 1.0) * blend

                if global_result is not None:
                    gr, gg, gb = global_result
                    gmean = (gr + gg + gb) / 3.0
                    if gmean > 0:
                        rr = gr / gmean
                        rg = gg / gmean
                        rb = gb / gmean
                        yellow_green = (rg > 1.045 and rb < 0.90)
                        yellow = ((gr + gg) / max(2.0, 2.0 * gb)) > 1.16
                        blue_deficit = rb < 0.84
                        green_excess = rg > 1.07
                        red_deficit = rr < 0.88

                        if yellow_green or yellow or blue_deficit:
                            deficit = max(0.0, 1.0 - rb)
                            b_gain *= 1.0 + min(0.08, deficit * 0.28)
                            if green_excess or yellow_green:
                                g_gain *= max(0.96, 1.0 - min(0.04, max(0.0, rg - 1.0) * 0.28))
                            if red_deficit:
                                r_gain *= 1.0 + min(0.025, max(0.0, 1.0 - rr) * 0.16)
                            method += "+limited-yellow-green-fallback"
                        elif green_excess:
                            g_gain *= 0.985
                            method += "+limited-green-cast-fallback"

                r_gain = min(1.12, max(0.90, r_gain))
                g_gain = min(1.10, max(0.90, g_gain))
                b_gain = min(1.14, max(0.90, b_gain))

                norm = (r_gain + g_gain + b_gain) / 3.0
                if norm > 0:
                    r_gain /= norm
                    g_gain /= norm
                    b_gain /= norm

                if max(abs(r_gain - 1.0), abs(g_gain - 1.0), abs(b_gain - 1.0)) >= 0.008:
                    filters.append(
                        f"colorchannelmixer=rr={r_gain:.5f}:gg={g_gain:.5f}:bb={b_gain:.5f}"
                    )

                global_text = ""
                if global_result is not None:
                    global_text = f"; globalRGB={global_result[0]:.1f}/{global_result[1]:.1f}/{global_result[2]:.1f}"
                wb_text = (
                    f"method={method}; {source_counts}; referenceRGB={nr:.1f}/{ng:.1f}/{nb:.1f}"
                    f"{global_text}; cast={cast_strength:.3f}; gains={r_gain:.3f}/{g_gain:.3f}/{b_gain:.3f}"
                )
            else:
                wb_text = "no usable pixels for automatic white balance"

        p10 = self._percentile_value(all_luma, 0.10)
        p50 = self._percentile_value(all_luma, 0.50)
        p90 = self._percentile_value(all_luma, 0.90)
        sat25 = self._percentile_value(all_sat, 0.25)
        sat50 = self._percentile_value(all_sat, 0.50)
        sat75 = self._percentile_value(all_sat, 0.75)
        sat90 = self._percentile_value(all_sat, 0.90)
        low_sat_fraction = (
            sum(1 for x in all_sat if x < 0.12) / float(len(all_sat))
            if all_sat else 0.0
        )

        eq_parts = []

        color_text = "Color=not requested"
        if color == "Auto":
            contrast = 1.0
            saturation = 1.0
            vibrance = 0.0
            color_mode = "normal"

            if p10 is not None and p90 is not None:
                spread = p90 - p10
                if spread < 65.0:
                    contrast = 1.08
                elif spread < 85.0:
                    contrast = 1.06
                elif spread < 110.0:
                    contrast = 1.04
                elif spread < 135.0:
                    contrast = 1.02
                elif spread > 215.0:
                    contrast = 0.97

            if sat50 is not None:
                severe_fade = (
                    sat50 < 0.10
                    and (sat75 is None or sat75 < 0.28)
                    and low_sat_fraction >= 0.45
                )
                strong_fade = (
                    sat50 < 0.16
                    and (sat75 is None or sat75 < 0.34)
                    and low_sat_fraction >= 0.35
                )
                mild_fade = sat50 < 0.24 and low_sat_fraction >= 0.25

                if severe_fade:
                    color_mode = "severe-fade source-preserve"
                    saturation = 1.045
                    vibrance = 0.35
                    if sat90 is not None and sat90 < 0.40:
                        vibrance = 0.45
                    elif sat90 is not None and sat90 < 0.52:
                        vibrance = 0.40
                elif strong_fade:
                    color_mode = "strong-fade source-preserve"
                    saturation = 1.035
                    vibrance = 0.25
                elif mild_fade:
                    color_mode = "mild-fade source-preserve"
                    saturation = 1.020
                    vibrance = 0.15
                else:
                    if sat50 < 0.30:
                        saturation = 1.020
                    elif sat50 < 0.36:
                        saturation = 1.010
                    elif sat50 > 0.64:
                        saturation = 0.97
                    elif sat50 > 0.52:
                        saturation = 0.99

                if sat90 is not None and sat90 > 0.72:
                    vibrance = min(vibrance, 0.10)
                    saturation = min(saturation, 1.00)

            saturation = min(1.05, max(0.95, saturation))
            vibrance = min(0.45, max(0.0, vibrance))

            if abs(contrast - 1.0) >= 0.005:
                eq_parts.append(f"contrast={contrast:.4f}")
            if abs(saturation - 1.0) >= 0.005:
                eq_parts.append(f"saturation={saturation:.4f}")

            if vibrance >= 0.05:
                filters.append(
                    f"vibrance=intensity={vibrance:.4f}:rbal=1.0000:gbal=1.0000:bbal=1.0000"
                )

            color_text = (
                f"mode={color_mode}; contrast={contrast:.3f}; saturation={saturation:.3f}; "
                f"vibrance={vibrance:.3f}; sat25/50/75/90="
                f"{sat25:.3f}/{sat50:.3f}/{sat75:.3f}/{sat90:.3f}; "
                f"lowSat={low_sat_fraction:.3f}"
                if None not in (sat25, sat50, sat75, sat90)
                else f"mode={color_mode}; contrast={contrast:.3f}; saturation={saturation:.3f}; "
                     f"vibrance={vibrance:.3f}; saturation stats unavailable"
            )

        brightness_text = "Brightness=not requested"
        if brightness == "Auto" and p50 is not None:
            adjust = 0.0

            if p50 < 72.0:
                adjust = min(0.070, (92.0 - p50) / 300.0)
            elif p50 < 92.0:
                adjust = min(0.045, (100.0 - p50) / 360.0)
            elif p50 > 188.0:
                adjust = max(-0.060, (166.0 - p50) / 360.0)
            elif p50 > 166.0:
                adjust = max(-0.035, (158.0 - p50) / 420.0)

            if abs(adjust) >= 0.002:
                eq_parts.append(f"brightness={adjust:.5f}")

            brightness_text = f"brightness={adjust:.4f}; luma50={p50:.1f}"

        if eq_parts:
            filters.append("eq=" + ":".join(eq_parts))

        luma_text = (
            f"luma10/50/90={p10:.1f}/{p50:.1f}/{p90:.1f}"
            if p10 is not None and p50 is not None and p90 is not None
            else "luma10/50/90=NA"
        )

        stats = (
            f"frames={sampled_frames}; {luma_text}; "
            f"{wb_text}; {color_text}; {brightness_text}"
        )

        return ",".join(filters), stats

    def _auto_sharpen_level(self, src: Path, info: VideoInfo) -> Tuple[str, str]:
        duration = max(0.0, float(info.duration or 0.0))
        if duration > 2.0:
            sample_times = [duration * x for x in (0.07, 0.23, 0.41, 0.59, 0.77, 0.93)]
        else:
            sample_times = [0.0]

        width = max(1, int(info.width or 1))
        height = max(1, int(info.height or 1))
        sample_w = min(320, width)
        sample_h = max(2, int(round((height * sample_w / width) / 2.0) * 2))

        frame_edge_means: List[float] = []
        frame_edge_p90: List[float] = []
        frame_flat_noise: List[float] = []

        for sample_time in sample_times:
            self._wait_if_paused()
            if self.stop_event.is_set():
                raise Cancelled()

            cmd = [
                self._tool(self.ffmpeg.get()),
                "-hide_banner", "-loglevel", "error",
                "-ss", f"{max(0.0, float(sample_time)):.3f}",
                "-i", str(src),
                "-frames:v", "1", "-an", "-sn",
                "-vf", f"scale={sample_w}:{sample_h}:flags=area,format=gray",
                "-f", "rawvideo", "pipe:1",
            ]
            try:
                cp = subprocess.run(
                    cmd, capture_output=True, text=False, timeout=45,
                    creationflags=self._no_window(),
                )
            except Exception:
                continue
            raw = cp.stdout if cp.returncode == 0 else b""
            if len(raw) < sample_w * sample_h:
                continue

            y = raw[: sample_w * sample_h]
            gradients: List[float] = []
            flat_residuals: List[float] = []

            for yy in range(1, sample_h - 1):
                base = yy * sample_w
                up = base - sample_w
                dn = base + sample_w
                for xx in range(1, sample_w - 1):
                    i = base + xx
                    c = y[i]
                    left = y[i - 1]
                    right = y[i + 1]
                    top = y[up + xx]
                    bottom = y[dn + xx]
                    gx = abs(int(right) - int(left))
                    gy = abs(int(bottom) - int(top))
                    g = 0.5 * (gx + gy)
                    gradients.append(g)
                    if g <= 10.0:
                        residual = abs(4 * int(c) - int(left) - int(right) - int(top) - int(bottom)) / 4.0
                        flat_residuals.append(residual)

            if not gradients:
                continue
            edge_mean = sum(gradients) / len(gradients)
            edge_p90 = self._percentile_value(gradients, 0.90)
            flat_noise = self._percentile_value(flat_residuals, 0.50) if flat_residuals else 0.0
            frame_edge_means.append(edge_mean)
            if edge_p90 is not None:
                frame_edge_p90.append(edge_p90)
            if flat_noise is not None:
                frame_flat_noise.append(flat_noise)

        if not frame_edge_means:
            return "Off", "frames=0; analysis unavailable; selected=Off"

        edge_mean = self._median_value(frame_edge_means) or 0.0
        edge_p90 = self._median_value(frame_edge_p90) or 0.0
        flat_noise = self._median_value(frame_flat_noise) or 0.0

        if flat_noise >= 7.5:
            level = "Off"
        elif edge_mean < 8.0 and edge_p90 < 24.0:
            level = "Medium"
        elif edge_mean < 20.0 and edge_p90 < 72.0:
            level = "Low"
        else:
            level = "Off"

        stats = (
            f"frames={len(frame_edge_means)}; edge_mean={edge_mean:.2f}; "
            f"edge_p90={edge_p90:.2f}; flat_noise={flat_noise:.2f}; selected={level}"
        )
        return level, stats

    def _prepare_output_correction_filters(self, job: Job, src: Path) -> List[str]:
        if not self._enhancement_is_enabled():
            self._post("log", "V261 ENHANCEMENT OFF: output correction filters bypassed.")
            return []
        color = self._job_setting("color_correction", self.color_correction)
        brightness = self._job_setting("brightness_correction", self.brightness_correction)
        white = self._job_setting("white_correction", self.white_correction)
        sharpen = str(self._job_setting("sharpen", self.sharpen) or "Off")
        deband = str(self._job_setting("deband", self.deband) or "Off")

        src_info = self._probe_video(src)
        sharpen_requested = sharpen
        sharpen_auto_stats = ""
        if sharpen.strip().casefold() == "auto":
            sharpen, sharpen_auto_stats = self._auto_sharpen_level(src, src_info)
            self._post("log", f"V169 AUTO SHARPEN: {sharpen_auto_stats}")

        self._post(
            "log",
            f"V169 ENHANCEMENT ANALYSIS: Color={color}; Brightness={brightness}; White balance={white}; "
            f"Sharpen={sharpen_requested}->{sharpen if sharpen_requested.casefold() == 'auto' else sharpen_requested}; Deband={deband}."
        )

        filters: List[str] = []

        auto_filter, auto_stats = self._static_auto_correction_filter(
            src, src_info, color, brightness, white
        )
        if auto_filter:
            filters.append(auto_filter)

        deband_map = {
            "low": "gradfun=strength=0.8:radius=12",
            "medium": "gradfun=strength=1.2:radius=16",
            "high": "gradfun=strength=1.6:radius=20",
        }
        deband_filter = deband_map.get(deband.strip().casefold())
        if deband_filter:
            filters.append(deband_filter)

        sharpen_map = {
            "low": "unsharp=5:5:0.35:5:5:0.0",
            "medium": "unsharp=5:5:0.60:5:5:0.0",
            "high": "unsharp=5:5:0.90:5:5:0.0",
        }
        sharpen_filter = sharpen_map.get(sharpen.strip().casefold())
        if sharpen_filter:
            filters.append(sharpen_filter)

        if not filters:
            if "Auto" in {color, brightness, white}:
                self._post(
                    "log",
                    f"V150 FIXED AUTO IMAGE CORRECTION: {auto_stats}; analysis completed and no pixel correction was necessary."
                )
            else:
                self._post("log", "Color/brightness/white/sharpen/deband correction: Off")
            return []

        vf = ",".join(filters)
        if "Auto" in {color, brightness, white}:
            self._post(
                "log",
                f"V150 FIXED AUTO IMAGE CORRECTION: {auto_stats}; correction will be fused into the final encode / RIFE output path."
            )
        self._post(
            "log",
            f"V150 LOW-LOSS ENHANCEMENT: Color={color}; Brightness={brightness}; White balance={white}; "
            f"Sharpen={sharpen_requested}->{sharpen if sharpen_requested.casefold() == 'auto' else sharpen_requested}; Deband={deband}; filters are merged into the final output encode; FFmpeg filter={vf}"
        )
        return filters

    def _comfy_launch_signature(self) -> Tuple[str, bool, bool]:
        if self._run_comfy_launch_mode is not None:
            return (
                str(self._run_comfy_launch_mode).strip() or "NVIDIA Fast",
                bool(self._run_comfy_disable_dynamic_vram),
                bool(self._run_comfy_disable_async_offload),
            )
        return (
            str(self._job_setting("comfy_launch_mode", self.comfy_launch_mode)).strip() or "NVIDIA Fast",
            bool(self.comfy_disable_dynamic_vram.get()),
            bool(self.comfy_disable_async_offload.get()),
        )

    def _comfy_mode_description(self) -> str:
        mode, disable_dynamic, disable_async = self._comfy_launch_signature()
        return (
            f"{mode} | DynamicVRAM {'OFF' if disable_dynamic else 'ON'} | "
            f"Async offload {'OFF' if disable_async else 'ON'}"
        )

    def _comfy_database_path(self) -> Path:
        root = Path(self.comfy_root.get().strip())
        return root / "ComfyUI" / "user" / "default" / f"upscaler_v77_{self._comfy_db_instance}.db"

    def _comfy_database_url(self) -> str:


        return "sqlite:///" + self._comfy_database_path().as_posix()

    def _legacy_custom_nodes_whitelist(self) -> Tuple[List[str], List[str]]:
        """Load the legacy custom nodes without importing the experimental
        SeedVR2.5 extension that crashes on some Windows/CUDA installations.

        Uses ComfyUI's native --disable-all-custom-nodes plus
        --whitelist-custom-nodes flags. This does NOT rename, delete, alter,
        or replace any installed files, and applies to this private process.
        """
        root = Path(self.comfy_root.get().strip()) / "ComfyUI" / "custom_nodes"
        if not root.is_dir():
            raise BackendError(
                "Legacy SeedVR2 requires ComfyUI custom nodes, but the directory "
                f"does not exist: {root}"
            )
        blocked = {"seedvr2_videoupscaler", "comfyui-seedvr2_videoupscaler"}
        whitelist: List[str] = []
        excluded: List[str] = []
        for entry in sorted(root.iterdir(), key=lambda x: x.name.casefold()):
            name = entry.name
            if name.startswith(".") or name == "__pycache__" or name.casefold().endswith(".disabled"):
                continue
            if not (entry.is_dir() or (entry.is_file() and entry.suffix.casefold() == ".py")):
                continue
            if name.casefold() in blocked:
                excluded.append(name)
                continue
            if entry.is_file() and name == "__init__.py":
                continue
            whitelist.append(name)
        # These nodes are required by the original SeedVR2 LongVideo API graph.
        for essential in ("ComfyUI-SeedVR2-LongVideo", "ComfyUI-VideoHelperSuite"):
            if essential.casefold() not in {n.casefold() for n in whitelist}:
                raise BackendError(
                    f"V222 LEGACY NODE ISOLATION: required custom node folder {essential!r} "
                    f"was not found in {root}. The experimental SeedVR2.5 node "
                    "will not be used as a replacement."
                )
        return whitelist, excluded

    def _comfy_base_command(self, port_override: Optional[int] = None) -> List[str]:
        root = Path(self.comfy_root.get().strip())
        py = root / "python_embeded" / "python.exe"
        main = root / "ComfyUI" / "main.py"
        port = int(port_override if port_override is not None else self.comfy_port.get())
        mode, disable_dynamic, disable_async = self._comfy_launch_signature()
        cmd = [
            str(py), "-s", "-u", str(main), "--windows-standalone-build",
            "--database-url", self._comfy_database_url(),


            "--cache-classic",
        ]
        if self._comfy_runtime_input_dir is not None:
            cmd += ["--input-directory", str(self._comfy_runtime_input_dir)]
        if self._comfy_runtime_output_dir is not None:
            cmd += ["--output-directory", str(self._comfy_runtime_output_dir)]
        if self._comfy_runtime_temp_dir is not None:
            cmd += ["--temp-directory", str(self._comfy_runtime_temp_dir)]
        if mode == "NVIDIA Fast":
            cmd += ["--fast", "fp16_accumulation"]
        # Real ComfyUI CLI flags, not cosmetic controls. Test one at a time.
        if disable_dynamic:
            cmd.append("--disable-dynamic-vram")
        if disable_async:
            cmd.append("--disable-async-offload")
        cmd += ["--listen", "127.0.0.1", "--port", str(port), "--disable-auto-launch"]
        # Exclude only the crashing experimental SeedVR2.5 extension from
        # this privately launched ComfyUI. The legacy workflow and other
        # installed custom nodes retain their original implementations.
        safe_nodes, _excluded = self._legacy_custom_nodes_whitelist()
        cmd.append("--disable-all-custom-nodes")
        if safe_nodes:
            cmd += ["--whitelist-custom-nodes", *safe_nodes]
        return cmd

    def _update_comfy_command_preview(self):
        try:
            cmd = self._comfy_base_command()
            self.comfy_command_preview.set(self._quote(cmd))
        except Exception:
            self.comfy_command_preview.set("Command preview unavailable until ComfyUI root/port are valid.")


    @staticmethod


    @staticmethod
    def _atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + f".tmp_{uuid.uuid4().hex[:8]}")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        os.replace(tmp, path)







    @staticmethod
    def _source_fingerprint(path: Path) -> Dict[str, Any]:
        st = path.stat()
        return {
            "path": str(path),
            "size": int(st.st_size),
            "mtime_ns": int(st.st_mtime_ns),
        }










    def _count_video_frames_exact(self, path: Path, strict: bool = False) -> int:
        """Count decoded video frames, rather than duration * rounded FPS.

        Neural workflows may request strict=True. Other legacy
        callers may retain the metadata fallback for other workflows.
        For instance, rounding 24000/1001 to 24 over a long clip invents
        dozens of frames and makes padded input fail verification.
        """
        path = Path(path)
        cmd = [
            self._tool(self.ffprobe.get()), "-v", "error", "-select_streams", "v:0",
            "-count_frames", "-show_entries", "stream=nb_read_frames",
            "-of", "default=nokey=1:noprint_wrappers=1", str(path),
        ]
        failure = "FFprobe did not return a decoded-frame count"
        try:
            cp = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                creationflags=self._no_window(),
            )
            if cp.returncode == 0:
                for line in (cp.stdout or "").splitlines():
                    try:
                        value = int(line.strip())
                        if value > 0:
                            return value
                    except (ValueError, TypeError):
                        pass
            else:
                failure = f"FFprobe exit code {cp.returncode}: {(cp.stderr or '').strip()[:300]}"
        except Exception as exc:
            failure = f"FFprobe could not run: {exc}"
        if strict:
            raise BackendError(
                f"Processing requires an exact decoded-frame count for {path.name}. "
                f"{failure}. Refusing to use duration multiplied by rounded FPS."
            )
        info = self._probe_video(path)
        return max(0, int(info.frames or 0))













    def _configured_comfy_port(self) -> int:
        return max(1, min(65535, int(self.comfy_port.get())))

    def _comfy_api_port(self) -> int:
        if self._comfy_runtime_port is not None:
            return int(self._comfy_runtime_port)
        return self._configured_comfy_port()

    @staticmethod
    def _local_port_in_use(port: int) -> bool:
        try:
            with socket.create_connection(("127.0.0.1", int(port)), timeout=0.35):
                return True
        except OSError:
            return False

    @staticmethod
    def _can_bind_local_port(port: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(("127.0.0.1", int(port)))
            return True
        except OSError:
            return False

    def _choose_private_comfy_port(self, preferred: int) -> int:
        preferred = max(1, min(65535, int(preferred)))
        if self._can_bind_local_port(preferred):
            return preferred

        for delta in range(1, 101):
            candidate = preferred + delta
            if candidate <= 65535 and self._can_bind_local_port(candidate):
                return candidate

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    def _wait_for_comfy_port_state(self, want_up: bool, timeout: float = 8.0, port: Optional[int] = None) -> bool:
        target_port = int(port if port is not None else self._comfy_api_port())
        deadline = time.time() + max(0.5, float(timeout))
        while time.time() < deadline:
            is_up = self._comfy_ping(target_port)
            if is_up == bool(want_up):
                return True
            if self.stop_event.is_set() and want_up:
                return False
            time.sleep(0.25)
        return self._comfy_ping(target_port) == bool(want_up)

    def _clear_managed_comfy_tracking(self):
        self.comfy_proc = None
        self._comfy_running_mode = None
        self._comfy_running_signature = None
        self._comfy_runtime_port = None
        self._comfy_runtime_root = None
        self._comfy_runtime_input_dir = None
        self._comfy_runtime_output_dir = None
        self._comfy_runtime_temp_dir = None
        self.comfy_console_thread = None

    def _clear_all_seedvr2_console_state(self) -> None:
        with self._seed_console_lock:
            self._seed_console_active_token = None
            self._seed_console_source_seen = False
            self._seed_console_final_by_token.clear()

    def _prepare_private_comfy_runtime_dirs(self) -> None:
        root = Path(self.comfy_root.get().strip())
        base = (
            root / "ComfyUI" / "Upscaler_V141_Runtime"
            / self._comfy_db_instance
            / uuid.uuid4().hex[:12]
        )
        input_dir = base / "input"
        output_dir = base / "output"
        temp_dir = base / "temp"
        for p in (input_dir, output_dir, temp_dir):
            p.mkdir(parents=True, exist_ok=True)
        self._comfy_runtime_root = base
        self._comfy_runtime_input_dir = input_dir
        self._comfy_runtime_output_dir = output_dir
        self._comfy_runtime_temp_dir = temp_dir
        if base not in self._comfy_runtime_dirs_to_cleanup:
            self._comfy_runtime_dirs_to_cleanup.append(base)

    def _stop_managed_comfy(self, reason: str = "", wait_port: bool = True) -> None:
        proc = self.comfy_proc
        runtime_port = self._comfy_runtime_port
        reader = self.comfy_console_thread


        self._comfy_generation += 1

        if proc is not None and proc.poll() is None:
            if reason:
                self._post("log", reason)
            self._terminate_tree(proc)
            try:
                proc.wait(timeout=8)
            except Exception:
                pass

        if reader is not None and reader is not threading.current_thread():
            try:
                reader.join(timeout=2.0)
            except Exception:
                pass

        self._clear_all_seedvr2_console_state()
        self._clear_managed_comfy_tracking()

        if wait_port and runtime_port is not None:
            self._wait_for_comfy_port_state(False, timeout=8.0, port=runtime_port)

    def _retain_comfy_input(self, path: Optional[Path]) -> None:
        if not path:
            return
        p = Path(path)
        if p not in self._comfy_retained_inputs:
            self._comfy_retained_inputs.append(p)

    def _cleanup_retained_comfy_inputs(self) -> None:
        if self.comfy_proc is not None and self.comfy_proc.poll() is None:

            return

        paths = list(self._comfy_retained_inputs)
        self._comfy_retained_inputs.clear()
        removed = 0
        for p in paths:
            try:
                if p.exists():
                    p.unlink()
                    removed += 1
            except Exception as e:
                self._post("log", f"V62 cleanup warning: could not delete retained ComfyUI input {p}: {e}")

        runtime_dirs = list(self._comfy_runtime_dirs_to_cleanup)
        self._comfy_runtime_dirs_to_cleanup.clear()
        dirs_removed = 0
        for d in runtime_dirs:
            try:
                if d.exists():
                    shutil.rmtree(d, ignore_errors=False)
                    dirs_removed += 1
            except Exception as e:
                self._post("log", f"V62 cleanup warning: could not delete private ComfyUI runtime folder {d}: {e}")

        if removed or dirs_removed:
            self._post(
                "log",
                f"V62 cleanup: removed {removed} retained input file(s) and "
                f"{dirs_removed} private ComfyUI runtime folder(s) after backend shutdown."
            )

    def _ensure_hidden_comfy(self):
        self._wait_if_paused()
        desired_mode = self._job_setting("comfy_launch_mode", self.comfy_launch_mode).strip() or "Standard NVIDIA"
        desired_signature = self._comfy_launch_signature()
        desired_description = self._comfy_mode_description()
        preferred_port = self._configured_comfy_port()


        if self.comfy_proc is not None and self.comfy_proc.poll() is not None:
            self._clear_managed_comfy_tracking()


        if self.comfy_proc is not None and self.comfy_proc.poll() is None:
            runtime_port = self._comfy_api_port()
            if self._comfy_ping(runtime_port) and self._comfy_running_signature == desired_signature:
                self._post(
                    "comfy_status",
                    f"Hidden ComfyUI: V62-owned on 127.0.0.1:{runtime_port} [{desired_description}]"
                )
                return

            if self._comfy_running_signature != desired_signature:
                old_desc = str(self._comfy_running_signature) if self._comfy_running_signature else "unknown"
                reason = (
                    f"ComfyUI launch options changed: {old_desc} -> {desired_description}. "
                    "Restarting the V62-owned backend..."
                )
            else:
                reason = "V62-owned ComfyUI is alive but its API is not responding. Restarting it..."
            self._stop_managed_comfy(reason=reason, wait_port=True)


        occupied = self._local_port_in_use(preferred_port)
        runtime_port = self._choose_private_comfy_port(preferred_port)
        if occupied and runtime_port != preferred_port:
            kind = "another ComfyUI API" if self._comfy_ping(preferred_port) else "another local process"
            self._post(
                "log",
                f"ENGINE SWITCH V62: preferred port {preferred_port} is occupied by {kind}. "
                f"V62 will NOT attach SeedVR2 to it; launching a clean owned ComfyUI on 127.0.0.1:{runtime_port}."
            )

        root = Path(self.comfy_root.get().strip())
        py = root / "python_embeded" / "python.exe"
        main = root / "ComfyUI" / "main.py"
        if not py.is_file() or not main.is_file():
            raise BackendError(f"ComfyUI portable installation not found under: {root}")

        try:
            self._comfy_database_path().parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise BackendError(f"Could not create the private V62 ComfyUI database directory: {e}")

        self._comfy_runtime_port = runtime_port
        self._prepare_private_comfy_runtime_dirs()
        cmd = self._comfy_base_command(runtime_port)
        allowed_nodes, excluded_nodes = self._legacy_custom_nodes_whitelist()
        self._post(
            "log",
            f"V222 LEGACY NODE ISOLATION: ComfyUI custom-node whitelist "
            f"({len(allowed_nodes)} allowed, {len(excluded_nodes)} experimental "
            f"SeedVR2.5 nodes excluded). "
            f"Excluded: {', '.join(excluded_nodes) if excluded_nodes else 'none found'}. "
            "Installed custom-node files were NOT modified."
        )
        self._post(
            "log",
            f"Starting clean V62-owned hidden ComfyUI backend on 127.0.0.1:{runtime_port} [{desired_description}]..."
        )
        self._post("log", "ComfyUI command: " + self._quote(cmd))
        flags = self._no_window() | (subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0)
        comfy_env = os.environ.copy()
        # ComfyUI's custom-node imports print Unicode symbols; Windows cp1252
        # cannot encode them when the Python subprocess has redirected stdout.
        # Set the child's standard streams to UTF-8 without altering the
        # Windows system code page or the user's global environment.
        comfy_env["PYTHONIOENCODING"] = "utf-8"
        comfy_env["PYTHONUTF8"] = "1"
        self.comfy_proc = subprocess.Popen(
            cmd, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
            creationflags=flags, env=comfy_env
        )
        self._comfy_running_mode = desired_mode
        self._comfy_running_signature = desired_signature

        self._comfy_generation += 1
        generation = self._comfy_generation
        proc_for_reader = self.comfy_proc
        self.comfy_console_thread = threading.Thread(
            target=self._read_comfy_console,
            args=(proc_for_reader, generation),
            daemon=True,
        )
        self.comfy_console_thread.start()

        deadline = time.time() + 120
        while time.time() < deadline:
            paused_for = self._wait_if_paused()
            deadline += paused_for
            if self.stop_event.is_set():
                self._stop_managed_comfy(reason="SeedVR2 startup cancelled; stopping V62-owned ComfyUI.")
                raise Cancelled()
            proc = self.comfy_proc
            if proc is None or proc.poll() is not None:
                self._clear_managed_comfy_tracking()
                raise BackendError("Hidden ComfyUI exited during startup. See the live log.")
            if self._comfy_ping(runtime_port):
                self._post(
                    "comfy_status",
                    f"Hidden ComfyUI: V62-owned on 127.0.0.1:{runtime_port} [{desired_description}]"
                )
                return
            time.sleep(0.5)
        self._stop_managed_comfy(reason="Hidden ComfyUI startup timed out; stopping V62-owned backend.")
        raise BackendError("Hidden ComfyUI did not become ready within 120 seconds.")

    def _read_comfy_console(self, proc: subprocess.Popen, generation: int):
        if not proc or not proc.stdout:
            return

        meta_re = re.compile(r"Meta-Batch\s+(\d+)\s*/\s*(\d+)", re.I)
        final_re = re.compile(r"Final muxed video:\s*(.+)$", re.I)
        source_re = re.compile(
            r"\[SeedVR2 Long Video\]\s+([^:\r\n]+?\.(?:mp4|mkv|mov|avi|m4v|mpeg|mpg|mts|m2ts|ts|webm|wmv|flv|vob|3gp)):\s",
            re.I,
        )
        prompt_time_re = re.compile(
            r"Prompt executed in\s+([0-9]+(?:\.[0-9]+)?)\s+seconds",
            re.I,
        )

        oom_terms = (
            "cuda out of memory",
            "outofmemoryerror",
            "out of memory",
            "failed to allocate",
            "memory allocation failed",
            "not enough memory",
        )

        for raw in proc.stdout:


            if generation != self._comfy_generation:
                continue

            line = raw.rstrip("\r\n")
            if not line:
                continue

            self._post("log", f"[ComfyUI] {line}")
            low = line.lower()

            sm = source_re.search(line)
            if sm:
                token = Path(sm.group(1).strip().strip('"')).name
                with self._seed_console_lock:
                    expected = self._seed_console_active_token
                    if expected and token.lower() == expected.lower():
                        self._seed_console_source_seen = True

                if expected and token.lower() == expected.lower():
                    self._post("log", f"SEEDVR2 V62 TOKEN START VERIFIED: {token}")
                else:
                    self._post(
                        "log",
                        f"SEEDVR2 V62 ignored unexpected Long Video source token: "
                        f"{token}; active token={expected or '--'}",
                    )

            if self.comfy_job_active and any(term in low for term in oom_terms):
                if not self._seed_spill_trigger:
                    self._post(
                        "log",
                        "VRAM SAFETY: actual CUDA/ComfyUI memory-allocation failure detected; "
                        "the attempt will be retried with a smaller temporal batch.",
                    )
                self._seed_spill_trigger = True

            tm = prompt_time_re.search(line)
            if tm and self.comfy_job_active:
                try:
                    seconds = float(tm.group(1))
                    self._seed_last_prompt_seconds = seconds
                    self._seed_batch_times.append(seconds)
                    if len(self._seed_batch_times) > 20:
                        self._seed_batch_times = self._seed_batch_times[-20:]
                except Exception:
                    pass

            m = meta_re.search(line)
            if m and self.comfy_job_active:
                a, b = int(m.group(1)), max(1, int(m.group(2)))
                self._seed_last_meta_batch = a
                self._seed_expected_meta_batches = b
                if a > b:
                    self._seed_meta_overrun = True
                self.comfy_seed_progress = min(0.99, min(a, b) / b)
                self._post("seed_progress", self.comfy_seed_progress)

            fm = final_re.search(line)
            if fm:
                p = Path(fm.group(1).strip().strip('"'))
                paired_token: Optional[str] = None
                source_seen = False

                with self._seed_console_lock:
                    if generation == self._comfy_generation:
                        paired_token = self._seed_console_active_token
                        source_seen = bool(self._seed_console_source_seen)
                        if paired_token and source_seen:
                            self._seed_console_final_by_token[paired_token.lower()] = p

                if paired_token and source_seen:
                    self.comfy_final_path = p
                    self.comfy_final_event.set()
                    self._post(
                        "log",
                        f"SEEDVR2 V62 TOKEN FINAL: {paired_token} -> {p}",
                    )
                elif paired_token:
                    self._post(
                        "log",
                        f"SEEDVR2 V176 ignored delayed/stale Final mux before source-token verification: "
                        f"{p}; active token={paired_token}",
                    )
                else:
                    self._post(
                        "log",
                        f"SEEDVR2 V62 ignored Final mux with no active token: {p}",
                    )

            if self.comfy_job_active and (
                "exception during processing" in low
                or "prompt outputs failed validation" in low
            ):
                if not self._seed_spill_trigger:
                    self.comfy_prompt_error = line

    def _comfy_ping(self, port: Optional[int] = None) -> bool:
        target_port = int(port if port is not None else self._comfy_api_port())
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{target_port}/system_stats", timeout=1.0) as r:
                return r.status == 200
        except Exception:
            return False

    def _load_api_workflow(self) -> Dict[str, Any]:
        p = Path(self.workflow_json.get().strip())
        if not p.is_file():
            raise BackendError("Select the API-format SeedVR2 workflow JSON in Tools / ComfyUI.")
        data = json.loads(p.read_text(encoding="utf-8-sig"))
        if "prompt" in data and isinstance(data["prompt"], dict):
            data = data["prompt"]

        if not isinstance(data, dict) or not data or not all(isinstance(v, dict) and "class_type" in v and "inputs" in v for v in data.values()):
            raise BackendError("The selected workflow is not ComfyUI API format. Export your working SeedVR2 workflow once as API format, then select it here.")
        return data

    def _refresh_seed_effective_preview(self) -> None:
        """Render the actual automatic policy and a live per-queued-video resolution plan.

        The preview is advisory until the pre-AI preprocessing is materialized.
        Runtime logs retain authoritative effective parameters after OOM backoff.
        """
        table = getattr(self, "seed_effective_table", None)
        if table is None:
            return
        # Current GUI controls apply to currently selected jobs; the rest retain
        # their own snapshotted Section #2 settings.
        try:
            selected = self._selected_jobs_from_table()
            profile_mode = str(self._job_setting("seed_parameter_mode", self.seed_parameter_mode))
            self.seed_effective_summary.set(
                ("Auto by AI output resolution (1080p: 37 / 2 / 512 / 32). "
                 "Only batch changes with resolution; overlaps/tile retain quality-tested defaults."
                 if profile_mode == SEED_PARAMETER_MODES[0]
                 else "Manual: use the four settings shown above for the selected file(s).")
            )
            # Auto values are computed, not silently written over manual choices.
            editable = profile_mode != SEED_PARAMETER_MODES[0]
            for combo in (self.seed_batch_box, self.seed_overlap_box,
                          self.seed_tile_box, self.seed_vae_overlap_box):
                combo.configure(state="normal" if editable else "disabled")
            table.delete(*table.get_children())
            if not self.jobs:
                # Always show example effective settings, even with an empty queue.
                examples = (("480p example", 854, 480), ("720p example", 1280, 720),
                            ("1080p default", 1920, 1080), ("1440p example", 2560, 1440),
                            ("2160p example", 3840, 2160))
                for name, w, h in examples:
                    synthetic = VideoInfo(path=Path(name), width=w, height=h,
                                          fps=30.0, duration=10.0, frames=300)
                    if profile_mode == SEED_PARAMETER_MODES[0]:
                        manual_batch, temporal, tile, spatial = None, 2, 512, 32
                    else:
                        manual_batch, temporal, tile, spatial = self._seed_user_controls()
                    batch, auto_temporal = self._auto_seed_temporal_params(synthetic, 1.0, manual_batch)
                    temporal = temporal if temporal is not None else auto_temporal
                    table.insert("", "end", values=(name, f"{w} x {h}", batch,
                                                       temporal, tile, spatial if spatial is not None else "Auto"))
                return
            for job in self.jobs:
                try:
                    def read_plan():
                        source = self._effective_upscale_info(job.info)
                        out_w, out_h = self._planned_ai_output_geometry(source)
                        # Runtime formula uses pre-AI input geometry times SeedVR2 factor;
                        # AI output geometry yields the same pixel workload for a direct job.
                        synth = VideoInfo(path=job.info.path, width=out_w, height=out_h,
                                          fps=source.fps, duration=source.duration, frames=source.frames)
                        man_batch, man_overlap, tile, spatial = self._seed_user_controls(job)
                        batch, auto_overlap = self._auto_seed_temporal_params(synth, 1.0, man_batch)
                        overlap = man_overlap if man_overlap is not None else auto_overlap
                        return out_w, out_h, batch, overlap, tile, spatial
                    w, h, batch, overlap, tile, spatial = self._job_settings_call(job, read_plan)
                    values = (job.info.path.name, f"{w} x {h}", batch,
                              overlap, tile, spatial if spatial is not None else "Auto")
                except Exception as exc:
                    values = (job.info.path.name, "Preview unavailable", "-", "-", "-", str(exc)[:40])
                table.insert("", "end", values=values)
        except (tk.TclError, AttributeError):
            pass

    def _seed_user_controls(self, job: Optional[Job] = None) -> Tuple[Optional[int], Optional[int], int, Optional[int]]:
        def setting(name: str, var: tk.Variable) -> str:
            if job is None:
                return str(var.get()).strip()
            return str(self._job_settings_call(job, lambda: self._job_setting(name, var))).strip()

        mode = setting("seed_parameter_mode", self.seed_parameter_mode)
        if mode == SEED_PARAMETER_MODES[0]:
            return None, 2, 512, 32

        batch_raw = setting("seed_batch_max", self.seed_batch_max)
        overlap_raw = setting("seed_temporal_overlap", self.seed_temporal_overlap)
        tile_raw = setting("seed_vae_tile", self.seed_vae_tile)
        spatial_raw = setting("seed_vae_spatial_overlap", self.seed_vae_spatial_overlap)

        def optional_int(raw: str, name: str, low: int, high: int) -> Optional[int]:
            if not raw or raw.lower() == "auto":
                return None
            try:
                value = int(raw)
            except ValueError:
                raise BackendError(f"SeedVR2 {name} must be an integer or Auto: {raw!r}.")
            if not low <= value <= high:
                raise BackendError(f"SeedVR2 {name} must be from {low} to {high}.")
            return value

        batch = optional_int(batch_raw, "max batch", 5, SEED_REF_BATCH)
        if batch is not None:
            batch = max((v for v in SEED_BATCHES if v <= batch), default=5)
        overlap = optional_int(overlap_raw, "temporal overlap", 0, 12)
        tile = optional_int(tile_raw, "VAE tile size", 256, 2048)
        tile = tile if tile is not None else 512
        if tile % 64:
            raise BackendError("SeedVR2 VAE tile size must be a multiple of 64 pixels.")
        spatial = optional_int(spatial_raw, "VAE spatial overlap", 0, 1024)
        if spatial is not None and spatial % 32:
            raise BackendError("SeedVR2 VAE spatial overlap must be in increments of 32 pixels (0, 32, 64, ...).")
        if spatial is not None and spatial >= tile:
            raise BackendError("SeedVR2 VAE spatial overlap must be smaller than the VAE tile size.")
        return batch, overlap, tile, spatial

    def _auto_seed_temporal_params(self, info: VideoInfo, factor: float, batch_override: Optional[int] = None) -> Tuple[int, int]:
        fps = info.fps if info.fps and info.fps > 1 else 25.0
        out_pixels = max(1, int(round(float(info.width) * float(info.height) * max(1.0, float(factor)) ** 2)))
        if batch_override is None:
            raw = int(math.floor(SEED_AUTO_1080P_PIXEL_FRAMES / float(out_pixels)))
            raw = max(5, min(SEED_REF_BATCH, raw))
            batch = max((b for b in SEED_BATCHES if b <= raw), default=5)
        else:
            requested = max(5, min(SEED_REF_BATCH, int(batch_override)))
            batch = max((b for b in SEED_BATCHES if b <= requested), default=5)


        overlap = int(round(8.0 * fps / 25.0))
        overlap = max(4, min(12, overlap))
        overlap = max(4, (overlap // 4) * 4)


        if batch < 29:
            overlap = 4
        overlap = min(12, overlap)
        return batch, overlap

    def _next_safer_seed_batch(self, current: int) -> int:
        current = max(5, int(current))
        target = max(5, int(math.floor(current * 0.70)))
        return max((b for b in SEED_BATCHES if b <= target), default=5)

    def _wait_for_gpu_release(self, timeout: float = 15.0) -> None:
        deadline = time.time() + max(1.0, float(timeout))
        last_used = None
        while time.time() < deadline:
            if self.stop_event.is_set():
                return
            stats = self._read_nvidia_stats()
            if stats is None:
                time.sleep(0.75)
                continue
            _gpu, used_mib, total_mib = stats
            last_used = used_mib


            if total_mib > 0 and used_mib <= total_mib * 0.35:
                self._post("log", f"VRAM SAFETY: GPU released to {used_mib/1024.0:.2f}/{total_mib/1024.0:.2f} GB before retry.")
                return
            time.sleep(0.75)
        if last_used is not None:
            self._post("log", f"VRAM SAFETY: retrying after release wait; dedicated VRAM still {last_used/1024.0:.2f} GB.")

    def _prepare_api_workflow(self, src_for_comfy: Path, factor: float, info: VideoInfo, batch_override: Optional[int] = None, job: Optional[Job] = None) -> Tuple[Dict[str, Any], Optional[Path]]:
        wf = copy.deepcopy(self._load_api_workflow())
        root = Path(self.comfy_root.get().strip())
        input_dir = self._comfy_runtime_input_dir or (root / "ComfyUI" / "input")
        input_dir.mkdir(parents=True, exist_ok=True)


        source_suffix = src_for_comfy.suffix.lower()
        source_vcodec = str(getattr(info, "vcodec", "") or "").strip().lower()
        seed_direct_suffixes = {".mp4", ".mkv", ".mov", ".avi", ".m4v", ".webm"}
        legacy_decode_codecs = {
            "vp6", "vp6f", "vp6a", "flv1", "svq1", "svq3",
            "msmpeg4v1", "msmpeg4v2", "msmpeg4v3", "cinepak",
            "indeo3", "indeo4", "indeo5"
        }

        force_legacy_transcode = source_vcodec in legacy_decode_codecs

        if source_suffix in seed_direct_suffixes and not force_legacy_transcode:
            token = f"UpscalerV62_{uuid.uuid4().hex[:10]}{source_suffix}"
            copied = input_dir / token
            shutil.copy2(src_for_comfy, copied)
        else:
            token = f"UpscalerV62_{uuid.uuid4().hex[:10]}.mkv"
            copied = input_dir / token
            cp = None

            if not force_legacy_transcode:
                remux_cmd = [
                    self._tool(self.ffmpeg.get()),
                    "-y", "-hide_banner", "-loglevel", "warning",
                    "-fflags", "+genpts+discardcorrupt",
                    "-err_detect", "ignore_err",
                    "-i", str(src_for_comfy),
                    "-map", "0:v:0",
                    "-an",
                    "-c:v", "copy",
                    "-avoid_negative_ts", "make_zero",
                    "-max_interleave_delta", "0",
                    str(copied),
                ]
                self._post(
                    "log",
                    f"V162 SEEDVR2 INPUT COMPATIBILITY: container={source_suffix or '<no extension>'}; codec={source_vcodec or 'unknown'}; attempting lossless stream-copy remux to MKV."
                )
                cp = subprocess.run(
                    remux_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=self._no_window(),
                )

            need_transcode = (
                force_legacy_transcode
                or cp is None
                or cp.returncode != 0
                or not copied.is_file()
                or copied.stat().st_size <= 0
            )

            if need_transcode:
                try:
                    copied.unlink(missing_ok=True)
                except Exception:
                    pass

                if force_legacy_transcode:
                    self._post(
                        "log",
                        f"V162 LEGACY CODEC PROTECTION: codec={source_vcodec or 'unknown'} is not passed through to SeedVR2. Decoding and rebuilding as lossless H.264 MKV to prevent black AI output."
                    )
                else:
                    self._post(
                        "log",
                        "V162 SEEDVR2 INPUT COMPATIBILITY: stream-copy remux failed; rebuilding a lossless H.264 MKV video stream for SeedVR2."
                    )

                transcode_cmd = [
                    self._tool(self.ffmpeg.get()),
                    "-y", "-hide_banner", "-loglevel", "warning",
                    "-fflags", "+genpts+discardcorrupt",
                    "-err_detect", "ignore_err",
                    "-i", str(src_for_comfy),
                    "-map", "0:v:0",
                    "-an",
                    "-vf", "setpts=PTS-STARTPTS",
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-crf", "0",
                    "-pix_fmt", "yuv420p",
                    "-fps_mode:v", "cfr",
                    str(copied),
                ]
                cp2 = subprocess.run(
                    transcode_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=self._no_window(),
                )
                if cp2.returncode != 0 or not copied.is_file() or copied.stat().st_size <= 0:
                    previous_err = ""
                    if cp is not None:
                        previous_err = cp.stderr or ""
                    detail = (cp2.stderr or previous_err or "").strip()
                    raise BackendError(
                        "Could not convert the source video to a SeedVR2-compatible H.264 MKV input."
                        + (f" FFmpeg: {detail[-1800:]}" if detail else "")
                    )

            self._post(
                "log",
                f"V162 SEEDVR2 INPUT COMPATIBILITY: staged compatible input as {token}; codec={source_vcodec or 'unknown'}."
            )

        self._validate_not_black_video(
            copied,
            f"SeedVR2 staged input {copied.name}"
        )

        scale_patch_details: List[str] = []
        manual_batch, manual_overlap, user_vae_tile, user_spatial_overlap = self._seed_user_controls(job)
        auto_batch, auto_overlap = self._auto_seed_temporal_params(info, factor, batch_override)
        selected_overlap = int(manual_overlap if manual_overlap is not None else auto_overlap)
        if selected_overlap >= auto_batch:
            raise BackendError(f"SeedVR2 temporal overlap {selected_overlap} must be less than batch {auto_batch}.")

        resize_nodes = [(nid, node) for nid, node in wf.items()
                        if str(node.get("class_type", "")).lower() == "resizeimagemasknode"]
        if len(resize_nodes) != 1:
            raise BackendError(f"Expected one conditioning resize node in the working legacy workflow; found {len(resize_nodes)}.")
        resize_id, resize_node = resize_nodes[0]
        resize_in = resize_node["inputs"]
        if abs(float(factor) - 1.0) < 1e-9:
            source_ref = resize_in.get("input")
            if not isinstance(source_ref, list) or len(source_ref) != 2:
                raise BackendError("Cannot bypass 1X conditioning: invalid resize source connection.")
            rewired = 0
            for node in wf.values():
                for k, v in node.get("inputs", {}).items():
                    if isinstance(v, list) and len(v) == 2 and str(v[0]) == str(resize_id):
                        node["inputs"][k] = list(source_ref)
                        rewired += 1
            if rewired < 2:
                raise BackendError("The 1X graph's resize references were not safely rewired.")
            del wf[resize_id]
            scale_field_found = True
            scale_patch_details.append(f"native 1X restoration; bypassed resize {resize_id}; rewired {rewired} links")
        else:
            target_w = self._even_dimension(info.width * float(factor))
            target_h = self._even_dimension(info.height * float(factor))
            resize_in["scale_method"] = "bicubic"
            for key in tuple(resize_in):
                if key.startswith("resize_type."):
                    resize_in.pop(key, None)
            if float(factor) > 8.0:
                if max(target_w, target_h) > 8192:
                    raise BackendError("Requested SeedVR2 dimensions exceed this ComfyUI resize node's 8192px limit.")
                resize_in.update({"resize_type": "scale dimensions", "resize_type.width": target_w,
                                  "resize_type.height": target_h, "resize_type.crop": "disabled"})
            else:
                resize_in.update({"resize_type": "scale by multiplier", "resize_type.multiplier": float(factor)})
            scale_field_found = True
            scale_patch_details.append(f"node {resize_id}:bicubic conditioning to {target_w}x{target_h}; one SeedVR2 diffusion pass")
        self._post("log", f"V221 SCALE: {factor:g}X; {'no enlargement' if factor == 1 else 'bicubic conditioning + AI reconstruction'}; no Lanczos enlargement, no second AI pass.")

        video_field_found = False
        temporal_field_found = False
        vae_spatial_patch_details: List[str] = []

        for node_id, node in wf.items():
            inputs = node.get("inputs", {})
            ct = str(node.get("class_type", "")).lower()


            if "vhs_batchmanager" in ct and "requeue" in inputs:
                try:
                    if int(inputs.get("requeue", 0)) != 0:
                        self._post(
                            "log",
                            f"V62 VHS reset: node {node_id} requeue "
                            f"{inputs.get('requeue')} -> 0 for a fresh video."
                        )
                    inputs["requeue"] = 0
                except Exception:
                    inputs["requeue"] = 0


            priority_node = ("seedvr2" in ct or "video" in ct or "load" in ct)
            if priority_node:
                for k in ("video", "filename", "file", "video_file"):
                    if k in inputs and isinstance(inputs[k], str):
                        inputs[k] = token
                        video_field_found = True
                        break
                if not video_field_found:
                    for k in ("video_path", "path", "file_path", "input_path"):
                        if k in inputs and isinstance(inputs[k], str):
                            inputs[k] = str(copied)
                            video_field_found = True
                            break


            multiplier_keys = {
                "scale_multiplier", "upscale_factor", "scale_factor",
                "resize_type.multiplier_1", "resize_type.multiplier",
            }
            for k in list(inputs.keys()):
                v = inputs.get(k)
                kl = str(k).lower()
                recognized_multiplier = (
                    kl in multiplier_keys
                    or (("resize_type" in kl or "upscale" in kl or "scale" in kl) and "multiplier" in kl)
                )
                if (str(node_id) != str(resize_id)
                        and recognized_multiplier and isinstance(v, (int, float)) and not isinstance(v, bool)):
                    old_value = float(v)
                    inputs[k] = float(factor)
                    scale_field_found = True
                    scale_patch_details.append(f"node {node_id}:{k} {old_value:g}->{float(factor):g}")


            if "seedvr2" in ct and "resolution" in inputs:
                v = inputs.get("resolution")
                if isinstance(v, (int, float)) and not isinstance(v, bool) and info.width > 0 and info.height > 0:
                    old_value = float(v)
                    shortest = self._even_dimension(min(info.width, info.height) * float(factor))
                    inputs["resolution"] = int(shortest)
                    scale_field_found = True
                    scale_patch_details.append(f"node {node_id}:resolution {old_value:g}->{int(shortest)}px-short-edge")

            is_vae_tiled = (
                "vaeencodetiled" in ct
                or "vaedecodetiled" in ct
                or ("vae" in ct and "tiled" in ct)
            )

            if is_vae_tiled:
                if "tile_size" in inputs:
                    old_tile = inputs["tile_size"]
                    inputs["tile_size"] = int(user_vae_tile)
                    vae_spatial_patch_details.append(f"{node_id} tile {old_tile}->{user_vae_tile}")
                if "overlap" in inputs and isinstance(inputs["overlap"], int) and not isinstance(inputs["overlap"], bool):
                    old = int(inputs["overlap"])
                    if user_spatial_overlap is None:
                        spatial = min(max(64, user_vae_tile - 32),
                                      max(old, min(256, max(128, user_vae_tile // 2))))
                    else:
                        spatial = int(user_spatial_overlap)
                    inputs["overlap"] = spatial
                    vae_spatial_patch_details.append(f"{node_id} spatial overlap {old}->{spatial}")

            for k in ("frames_per_batch", "batch_size"):
                if k in inputs and isinstance(inputs[k], int) and not isinstance(inputs[k], bool):
                    inputs[k] = int(auto_batch)
                    temporal_field_found = True

            if not is_vae_tiled:
                for k in ("overlap_frames", "temporal_overlap"):
                    if k in inputs and isinstance(inputs[k], int) and not isinstance(inputs[k], bool):
                        inputs[k] = int(selected_overlap)
                        temporal_field_found = True

                if (
                    "overlap" in inputs
                    and isinstance(inputs["overlap"], int)
                    and not isinstance(inputs["overlap"], bool)
                    and (
                        "longvideo" in ct
                        or "batchmanager" in ct
                        or "metabatch" in ct
                    )
                ):
                    inputs["overlap"] = int(selected_overlap)
                    temporal_field_found = True


            for k in ("chunk_seconds", "seconds_per_batch", "batch_seconds"):
                if k in inputs and isinstance(inputs[k], (int, float)) and not isinstance(inputs[k], bool):
                    inputs[k] = max(0.20, auto_batch / max(1.0, info.fps or 25.0))
                    temporal_field_found = True


            if "custom_width" in inputs and isinstance(inputs["custom_width"], (int, float)):
                inputs["custom_width"] = 0
            if "custom_height" in inputs and isinstance(inputs["custom_height"], (int, float)):
                inputs["custom_height"] = 0

        if not video_field_found:
            copied.unlink(missing_ok=True)
            raise BackendError("Could not locate a video/path input in the API workflow. Use the same working SeedVR2 LongVideo workflow you tested in ComfyUI.")
        if not scale_field_found:
            copied.unlink(missing_ok=True)
            raise BackendError(
                f"SeedVR2 requested {factor:g}X, but V62 could not identify a writable scale control in the API workflow. "
                "Processing was stopped rather than reusing an unknown/previous workflow scale. "
                "For SeedVR2 LongVideo v1.4, the expected API input is usually 'resize_type.multiplier_1' (UI label 'scale_multiplier')."
            )
        self._post(
            "log",
            f"SeedVR2 SCALE VERIFIED/PATCHED: requested={float(factor):g}X; " + "; ".join(scale_patch_details)
        )
        if vae_spatial_patch_details:
            self._post(
                "log",
                "V62 VAE SPATIAL SEAM FIX: " + "; ".join(vae_spatial_patch_details)
            )
        else:
            self._post(
                "log",
                "V62 VAE SPATIAL SEAM FIX: no tiled VAE spatial-overlap input was found in this API workflow."
            )

        if not temporal_field_found:
            self._post("log", "WARNING: Could not identify a direct SeedVR2 temporal control (frames/batch, temporal overlap or chunk_seconds). Automatic VRAM backoff may not change the actual workflow batch size.")
        else:
            self._post("log", f"SeedVR2 workflow patched: frames/batch={auto_batch}, temporal overlap={selected_overlap} (Auto).")

        return wf, copied

    def _seedvr2_expected_output_geometry(self, job: Job, factor: float) -> Tuple[int, int, VideoInfo]:
        # The AI operates on the preprocessed video, not necessarily on the
        # original file. This includes Lanczos downscaling, FPS conversion,
        # denoising, and each explicitly configured neural scaling stage.
        ai_ref = job.ai_info or job.info
        if ai_ref.width <= 0 or ai_ref.height <= 0:
            raise BackendError(
                f"Cannot validate SeedVR2 geometry: invalid AI input "
                f"{ai_ref.width}x{ai_ref.height}."
            )
        return (
            self._even_dimension(ai_ref.width * float(factor)),
            self._even_dimension(ai_ref.height * float(factor)),
            ai_ref,
        )

    def _verify_seedvr2_output_geometry(self, job: Job, output: Path, factor: float) -> None:
        try:
            got = self._probe_video(output)
        except Exception as e:
            raise BackendError(f"SeedVR2 output was created but its geometry could not be verified: {e}")
        expected_w, expected_h, ai_ref = self._seedvr2_expected_output_geometry(job, factor)

        if abs(got.width - expected_w) > 4 or abs(got.height - expected_h) > 4:
            raise BackendError(
                f"SeedVR2 SCALE MISMATCH: requested {factor:g}X from the actual AI input "
                f"{ai_ref.width}x{ai_ref.height} (original file: "
                f"{job.info.width}x{job.info.height}); expected about "
                f"{expected_w}x{expected_h}, but SeedVR2 produced "
                f"{got.width}x{got.height}. "
                "Output rejected because the scale differs from the current AI input's expected scale."
            )
        self._post(
            "log",
            f"SeedVR2 OUTPUT SCALE VERIFIED: requested={factor:g}X; "
            f"AI input={ai_ref.width}x{ai_ref.height}; original={job.info.width}x{job.info.height}; "
            f"output={got.width}x{got.height}; expected={expected_w}x{expected_h}."
        )

    def _submit_prompt(self, wf: Dict[str, Any]) -> str:
        payload = json.dumps({"prompt": wf, "client_id": uuid.uuid4().hex}).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{self._comfy_api_port()}/prompt",
            data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise BackendError(f"ComfyUI rejected the workflow: HTTP {e.code}: {body}")
        pid = data.get("prompt_id")
        if not pid:
            raise BackendError(f"ComfyUI did not return a prompt_id: {data}")
        return str(pid)

    def _comfy_prompt_history(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{self._comfy_api_port()}/history/{prompt_id}",
                timeout=3.0,
            ) as r:
                data = json.loads(r.read().decode("utf-8"))
        except Exception:
            return None
        if not isinstance(data, dict):
            return None
        record = data.get(prompt_id)
        if isinstance(record, dict):
            return record


        if len(data) == 1:
            only = next(iter(data.values()))
            if isinstance(only, dict):
                return only
        return None

    def _comfy_history_state(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        status = record.get("status", {}) if isinstance(record, dict) else {}
        if not isinstance(status, dict):
            status = {}
        status_str = str(status.get("status_str", "")).strip().lower()
        completed = bool(status.get("completed", False))
        failed = status_str in {"error", "failed", "failure"}


        messages = status.get("messages", [])
        error_text = ""
        try:
            if isinstance(messages, list):
                for item in reversed(messages):
                    blob = json.dumps(item, ensure_ascii=False)
                    low = blob.lower()
                    if "execution_error" in low or "error" in low or "exception" in low:
                        error_text = blob
                        break
        except Exception:
            error_text = ""

        if failed:
            return True, error_text or f"ComfyUI prompt finished with status '{status_str}'."
        if completed or status_str in {"success", "completed"}:
            return True, None
        return False, None

    def _history_video_paths(self, record: Dict[str, Any]) -> List[Path]:
        root = Path(self.comfy_root.get().strip()) / "ComfyUI"
        output_root = root / "output"
        temp_root = root / "temp"
        input_root = root / "input"
        found: List[Path] = []
        seen = set()

        def add_path(p: Path):
            try:
                key = str(p.resolve()).lower()
            except Exception:
                key = str(p).lower()
            if p.suffix.lower() in VIDEO_EXTENSIONS and key not in seen:
                seen.add(key)
                found.append(p)

        def walk(obj: Any):
            if isinstance(obj, dict):
                filename = obj.get("filename")
                if isinstance(filename, str) and Path(filename).suffix.lower() in VIDEO_EXTENSIONS:
                    raw = Path(filename)
                    if raw.is_absolute():
                        add_path(raw)
                    else:
                        sub = str(obj.get("subfolder", "") or "")
                        kind = str(obj.get("type", "output") or "output").lower()
                        base = output_root
                        if kind == "temp":
                            base = temp_root
                        elif kind == "input":
                            base = input_root
                        add_path(base / sub / raw)
                for value in obj.values():
                    walk(value)
            elif isinstance(obj, (list, tuple)):
                for value in obj:
                    walk(value)
            elif isinstance(obj, str):

                p = Path(obj.strip().strip('"'))
                if p.suffix.lower() in VIDEO_EXTENSIONS:
                    if p.is_absolute():
                        add_path(p)
                    else:
                        add_path(output_root / p)

        outputs = record.get("outputs", {}) if isinstance(record, dict) else {}
        walk(outputs)
        return found

    def _snapshot_comfy_video_outputs(self, output_root: Path) -> Dict[str, Tuple[int, int]]:
        snap: Dict[str, Tuple[int, int]] = {}
        try:
            for p in output_root.rglob("*"):
                if not p.is_file() or p.suffix.lower() not in VIDEO_EXTENSIONS:
                    continue
                try:
                    st = p.stat()
                    key = str(p.resolve()).lower()
                    snap[key] = (int(st.st_mtime_ns), int(st.st_size))
                except Exception:
                    continue
        except Exception:
            pass
        return snap

    def _changed_comfy_video_outputs(
        self,
        output_root: Path,
        before: Dict[str, Tuple[int, int]],
        submitted_at: float,
    ) -> List[Path]:
        changed: List[Tuple[int, Path]] = []
        try:
            for p in output_root.rglob("*"):
                if not p.is_file() or p.suffix.lower() not in VIDEO_EXTENSIONS:
                    continue
                try:
                    st = p.stat()
                    key = str(p.resolve()).lower()
                    sig = (int(st.st_mtime_ns), int(st.st_size))
                    old = before.get(key)

                    if (old is None or old != sig) and st.st_mtime >= submitted_at - 2.0 and st.st_size > 1024:
                        changed.append((int(st.st_mtime_ns), p))
                except Exception:
                    continue
        except Exception:
            pass
        changed.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in changed]

    def _pick_seedvr2_output_for_prompt(
        self,
        job: Job,
        factor: float,
        record: Dict[str, Any],
        output_root: Path,
        before: Dict[str, Tuple[int, int]],
        submitted_at: float,
        console_path: Optional[Path],
    ) -> Optional[Path]:
        expected_w = self._even_dimension(job.info.width * float(factor))
        expected_h = self._even_dimension(job.info.height * float(factor))
        ordered: List[Path] = []
        seen = set()

        def add(p: Optional[Path]):
            if not p:
                return
            try:
                key = str(p.resolve()).lower()
            except Exception:
                key = str(p).lower()
            if key not in seen:
                seen.add(key)
                ordered.append(p)


        for p in self._history_video_paths(record):
            add(p)


        changed = self._changed_comfy_video_outputs(output_root, before, submitted_at)
        changed_keys = set()
        for p in changed:
            try:
                changed_keys.add(str(p.resolve()).lower())
            except Exception:
                changed_keys.add(str(p).lower())
        if console_path:
            try:
                ck = str(console_path.resolve()).lower()
            except Exception:
                ck = str(console_path).lower()
            if ck in changed_keys:
                add(console_path)

        for p in changed:
            add(p)

        for p in ordered:
            if not p.exists() or p.suffix.lower() not in VIDEO_EXTENSIONS:
                continue
            try:
                info = self._probe_video(p)
            except Exception:
                continue
            if abs(info.width - expected_w) <= 4 and abs(info.height - expected_h) <= 4:
                return p
        return None

    @staticmethod
    def _seedvr2_full_length_check(actual: VideoInfo, reference: VideoInfo) -> Tuple[bool, str]:
        """Reject stable intermediate MetaBatch files; require essentially all AI input frames.

        A container may be finalized and probeable after EVERY MetaBatch.  File-size
        stability and correct width/height are not proof that the video is complete.
        Permit only ~2 frames of timing tolerance, not a percentage of the movie.
        """
        expected_duration = max(0.0, float(reference.duration or 0.0))
        expected_frames = max(0, int(reference.frames or 0))
        actual_duration = max(0.0, float(actual.duration or 0.0))
        actual_frames = max(0, int(actual.frames or 0))
        fps = float(reference.fps or actual.fps or 24.0)
        fps = fps if fps > 0 else 24.0
        # FFprobe container durations can differ by a frame or two; account for
        # timestamp rounding without accepting an incomplete batch.
        duration_tolerance = max(0.10, 2.5 / fps)
        frame_tolerance = 2
        details = (
            f"observed={actual_duration:.3f}s/{actual_frames or '?'} frames; "
            f"expected={expected_duration:.3f}s/{expected_frames or '?'} frames"
        )
        if expected_duration <= 0 and expected_frames <= 0:
            return False, f"AI input has no measurable expected duration/frame count ({details})"
        if expected_duration > 0:
            if actual_duration <= 0:
                return False, f"output duration not yet measurable ({details})"
            if actual_duration < expected_duration - duration_tolerance:
                return False, f"output is not yet full length ({details})"
        if expected_frames > 0:
            if actual_frames <= 0:
                # If duration is independently available, duration checking is
                # sufficient when the container does not expose a frame count.
                if expected_duration <= 0:
                    return False, f"output frame count not yet measurable ({details})"
            elif actual_frames < expected_frames - frame_tolerance:
                return False, f"output is missing frames ({details})"
        return True, details

    def _seedvr2_candidate_length_ready(
        self, info: VideoInfo, job: Job, path: Path, stable_state: Dict[str, Any]
    ) -> bool:
        ready, detail = self._seedvr2_full_length_check(info, job.ai_info or job.info)
        if not ready:
            # Log once per new observed length, not every 0.5-second polling cycle.
            if stable_state.get("incomplete_reported") != detail:
                stable_state["incomplete_reported"] = detail
                self._post(
                    "log",
                    f"V255 SEEDVR2 OUTPUT STILL INCOMPLETE: {detail}; "
                    f"waiting for remaining MetaBatches before accepting {path.name}."
                )
            return False
        stable_state.pop("incomplete_reported", None)
        return True

    def _probe_private_seedvr2_output_when_stable(
        self,
        path: Path,
        job: Job,
        expected_w: int,
        expected_h: int,
        stable_state: Dict[str, Any],
    ) -> Optional[Path]:
        try:
            if not path.exists():
                return None
            st = path.stat()
            if st.st_size <= 1024:
                return None
            sig = (int(st.st_size), int(st.st_mtime_ns))
        except Exception:
            return None

        if stable_state.get("sig") == sig:
            stable_state["count"] = int(stable_state.get("count", 0)) + 1
        else:
            stable_state["sig"] = sig
            stable_state["count"] = 0
            return None

        if int(stable_state.get("count", 0)) < 3:
            return None
        try:
            info = self._probe_video(path)
        except Exception:
            return None
        if abs(info.width - expected_w) > 4 or abs(info.height - expected_h) > 4:
            return None
        if not self._seedvr2_candidate_length_ready(info, job, path, stable_state):
            return None
        return path

    def _seedvr2_final_for_token(self, token: str) -> Optional[Path]:
        with self._seed_console_lock:
            return self._seed_console_final_by_token.get(str(token).lower())

    def _clear_seedvr2_token_state(self, token: str) -> None:
        with self._seed_console_lock:
            self._seed_console_final_by_token.clear()
            self._seed_console_active_token = str(token)
            self._seed_console_source_seen = False

    def _probe_seedvr2_final_when_stable(
        self,
        path: Path,
        job: Job,
        expected_w: int,
        expected_h: int,
        stable_state: Dict[str, Any],
        not_before: float = 0.0,
    ) -> Optional[Path]:
        try:
            if not path.exists() or path.stat().st_size <= 1024:
                return None
            st = path.stat()
            if not_before > 0.0 and float(st.st_mtime) + 1.0 < float(not_before):
                return None
            sig = (int(st.st_size), int(st.st_mtime_ns))
        except Exception:
            return None

        if stable_state.get("sig") == sig:
            stable_state["count"] = int(stable_state.get("count", 0)) + 1
        else:
            stable_state["sig"] = sig
            stable_state["count"] = 0
            return None


        if int(stable_state.get("count", 0)) < 2:
            return None

        try:
            info = self._probe_video(path)
        except Exception:
            return None

        if abs(info.width - expected_w) > 4 or abs(info.height - expected_h) > 4:
            mismatch = (int(info.width), int(info.height), int(expected_w), int(expected_h))
            if stable_state.get("mismatch") != mismatch:
                stable_state["mismatch"] = mismatch
                self._post(
                    "log",
                    f"SEEDVR2 V176 ignored stale/mismatched token-bound output: expected about "
                    f"{expected_w}x{expected_h}, observed {info.width}x{info.height}: {path}. "
                    "Continuing to wait for the current token's correct output."
                )
            return None
        stable_state.pop("mismatch", None)
        if not self._seedvr2_candidate_length_ready(info, job, path, stable_state):
            return None
        return path

    @staticmethod
    def _native_sr_read_png(fh) -> Optional[bytes]:
        """Return one complete PNG from an FFmpeg image2pipe, never modifying pixels."""
        def read_exact(size: int) -> bytes:
            data = bytearray()
            while len(data) < size:
                part = fh.read(size - len(data))
                if not part:
                    break
                data.extend(part)
            return bytes(data)
        sig = read_exact(8)
        if not sig:
            return None
        if sig != b"\x89PNG\r\n\x1a\n":
            raise BackendError("FFmpeg native SR decoder returned an invalid PNG stream.")
        parts = [sig]
        while True:
            header = read_exact(8)
            if len(header) != 8:
                raise BackendError("Truncated PNG header from native SR decoder.")
            length = int.from_bytes(header[:4], "big")
            if length > 256 * 1024 * 1024:
                raise BackendError("Unexpectedly large PNG chunk from native SR decoder.")
            payload = bytearray()
            remaining = length + 4
            while remaining:
                piece = fh.read(min(remaining, 1024 * 1024))
                if not piece:
                    raise BackendError("Truncated PNG payload from native SR decoder.")
                payload.extend(piece)
                remaining -= len(piece)
            parts.extend((header, bytes(payload)))
            if header[4:] == b"IEND":
                return b"".join(parts)

    @staticmethod
    def _native_sr_png_size(path: Path) -> Tuple[int, int]:
        with Path(path).open("rb") as fh:
            header = fh.read(24)
        if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
            raise BackendError(f"Native AI super-resolution did not produce a valid PNG: {path}")
        return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")

    def _run_basicvsr_ram_stream(self, job: Job, source: Path, temp_dir: Path,
                                 python_cmd: str, config: Path, checkpoint: Path,
                                 max_seq: Optional[int], chunk_frames: int,
                                 input_info: VideoInfo, out_w: int, out_h: int) -> Path:
        """Decode RGB24 -> model/overlap blending in RAM -> encode FFV1.

        Never write/read PNG frames or tile files. The lossless MKV is an actual
        output artifact required by the next scaling/restoration stage.
        """
        base=Path(temp_dir)/'V259_BasicVSR_RAM_4X'
        base.mkdir(parents=True,exist_ok=True)
        output=base/'BasicVSRPlusPlus_native_4X_lossless.mkv'
        fps=Fraction(float(input_info.fps)).limit_denominator(100100)
        fps_text=f'{fps.numerator}/{fps.denominator}'
        ffmpeg=self._tool(self.ffmpeg.get())
        decode_cmd=[ffmpeg,'-hide_banner','-loglevel','error','-i',str(source),
                    '-map','0:v:0','-an','-sn','-vsync','0',
                    '-pix_fmt','rgb24','-f','rawvideo','pipe:1']
        encode_cmd=[ffmpeg,'-y','-hide_banner','-loglevel','error',
                    '-f','rawvideo','-pixel_format','bgr24','-video_size',f'{out_w}x{out_h}',
                    '-framerate',fps_text,'-i','pipe:0',
                    '-an','-c:v','ffv1','-level','3','-pix_fmt','gbrp',
                    '-fps_mode','passthrough',str(output)]
        tile_profile=str(self._job_setting('basicvsr_tile_profile',self.basicvsr_tile_profile))
        # Cap float32 tile blending buffers to ~1.5 GB per work unit, even if
        # users request 120 frames/chunk. One 4X output frame uses 3 float32
        # channels plus a shared weighting mask.
        blend_bytes_per_frame=out_w*out_h*3*4
        ram_frames=max(1,int(1_500_000_000/max(1,blend_bytes_per_frame)))
        actual_chunk=max(1,min(int(chunk_frames),ram_frames))
        self._post('log',f'V259 BASICVSR++ RAM: decode RGB24 -> neural native 4X -> '
                           f'encode FFV1 BGR24. No PNGs, tiles or segment files; '
                           f'chunk={actual_chunk}, frame bytes={input_info.width*input_info.height*3:,}; '
                           f'tile profile={tile_profile}.')
        worker=BasicVSRRamWorker(self,job,python_cmd,config,checkpoint,base)
        decoder=encoder=None
        total=0
        frame_size=input_info.width*input_info.height*3
        job.native_vsr_frames_expected=max(1,int(input_info.frames or
            round(input_info.duration*input_info.fps) or 1))
        job.native_vsr_frames_done=0
        job.native_vsr_stage_eta_seconds=None
        expected_batches=max(1, math.ceil(job.native_vsr_frames_expected/actual_chunk))
        batch_index=0
        self._post('log', f'V260 BASICVSR++ PLAN: {job.native_vsr_frames_expected} input frames '
                          f'({input_info.fps:g} fps), up to {actual_chunk} frames per batch, '
                          f'{expected_batches} expected batches; output {out_w}x{out_h} (neural 4X).')
        began=self._job_elapsed_now(job)
        decoder_error=base/'ffmpeg_decode_errors.txt'
        encoder_error=base/'ffmpeg_encode_errors.txt'
        with decoder_error.open('wb') as de, encoder_error.open('wb') as ee:
            try:
                worker.start()
                decoder=subprocess.Popen(decode_cmd,stdout=subprocess.PIPE,stderr=de,
                                          bufsize=0,creationflags=self._no_window())
                encoder=subprocess.Popen(encode_cmd,stdin=subprocess.PIPE,stderr=ee,
                                          stdout=subprocess.DEVNULL,bufsize=0,
                                          creationflags=self._no_window())
                with self.process_lock:
                    self._aux_processes.extend((decoder,encoder))
                while True:
                    self._wait_if_paused()
                    if self.stop_event.is_set(): raise Cancelled()
                    frames=[]
                    for _ in range(actual_chunk):
                        first=decoder.stdout.read(frame_size)
                        if not first:
                            break
                        if len(first)<frame_size:
                            tail=bytearray(first)
                            while len(tail)<frame_size:
                                next_bytes=decoder.stdout.read(frame_size-len(tail))
                                if not next_bytes: break
                                tail.extend(next_bytes)
                            if len(tail)!=frame_size:
                                raise BackendError('FFmpeg decoded a truncated raw RGB frame')
                            first=bytes(tail)
                        frames.append(first)
                    if not frames: break
                    batch_index += 1
                    from_frame=total+1
                    to_frame=total+len(frames)
                    display_batches=max(expected_batches,batch_index)
                    self._post('log',
                        f'V260 BASICVSR++ BATCH {batch_index}/{display_batches} START: '
                        f'frames {from_frame}-{to_frame}/{job.native_vsr_frames_expected}; '
                        f'{len(frames)} frames in RAM; tile profile={tile_profile}.')
                    batch_started=self._job_elapsed_now(job)
                    self._post('step',
                        f'Current step: BasicVSR++ batch {batch_index}/{display_batches} '
                        f'INFERENCE | frames {from_frame}-{to_frame}/'
                        f'{job.native_vsr_frames_expected}')
                    worker.infer_to_encoder(frames,input_info.width,input_info.height,
                                            tile_profile,max_seq,encoder.stdin)
                    batch_seconds=max(0.001,self._job_elapsed_now(job)-batch_started)
                    total+=len(frames)
                    job.native_vsr_frames_done=total
                    expected=job.native_vsr_frames_expected
                    elapsed=max(.001,self._job_elapsed_now(job)-began)
                    fraction=min(1.,total/max(1,expected))
                    job.native_vsr_stage_eta_seconds=(elapsed/total*max(0,expected-total)
                                                       if total<expected else 0.0)
                    self._set_stage_fraction(job,.68*fraction)
                    self._post('step',
                        f'Current step: BasicVSR++ batch {batch_index}/{display_batches} DONE | '
                        f'{total}/{expected} frames ({fraction*100:.1f}%) | '
                        f'ETA {self._fmt_time(job.native_vsr_stage_eta_seconds)}')
                    self._post('log',
                        f'V260 BASICVSR++ BATCH {batch_index}/{display_batches} DONE: '
                        f'{total}/{expected} frames ({fraction*100:.1f}%) | '
                        f'batch={batch_seconds:.2f}s ({len(frames)/batch_seconds:.3f} fps) | '
                        f'cumulative={elapsed:.1f}s ({total/elapsed:.3f} fps) | '
                        f'ETA={self._fmt_time(job.native_vsr_stage_eta_seconds)} | '
                        f'GPU model loads=1 | RAM frames, no PNG files.')
                    del frames
                if decoder.stdout: decoder.stdout.close()
                if decoder.wait(timeout=120)!=0:
                    raise BackendError(f'V259 FFmpeg decoder failed: {decoder_error}')
                encoder.stdin.close()
                if encoder.wait(timeout=120)!=0:
                    raise BackendError(f'V259 lossless FFV1 encoding failed: {encoder_error}')
            finally:
                for process in (decoder,encoder):
                    if process is None: continue
                    if process.poll() is None:
                        self._terminate_tree(process)
                    for stream in (process.stdin,process.stdout):
                        if stream is not None:
                            try: stream.close()
                            except Exception: pass
                    with self.process_lock:
                        if process in self._aux_processes:
                            self._aux_processes.remove(process)
                worker.stop()
        if total<1:
            raise BackendError('BasicVSR++ RAM decoder returned no frames')
        if not output.is_file() or output.stat().st_size<1024:
            raise BackendError('BasicVSR++ RAM output FFV1 video was not created')
        verify=self._probe_video(output)
        if (verify.width,verify.height)!=(out_w,out_h):
            raise BackendError('BasicVSR++ RAM encoded output is not native 4X')
        if verify.frames and verify.frames!=total:
            raise BackendError(f'BasicVSR++ RAM output frames {verify.frames} != {total}')
        if abs(verify.fps-input_info.fps)>.02:
            raise BackendError('BasicVSR++ RAM output changed source FPS')
        job.stage_native_vsr_seconds+=max(0.0,self._job_elapsed_now(job)-began)
        job.native_vsr_stage_eta_seconds=0.
        self._set_stage_fraction(job,.70)
        self._post('log',
            f'V260 BASICVSR++ ALL BATCHES COMPLETE: {batch_index} batches, '
            f'{total} frames ({out_w}x{out_h}), neural stage='
            f'{self._fmt_time(self._job_elapsed_now(job)-began)}, '
            f'FFV1={output}; no intermediate PNG files.')
        return output

    def _run_native_neural_sr(
        self, job: Job, source: Path, temp_dir: Path, scale: int,
        requested_factor: Optional[float] = None, model_override: Optional[str] = None,
    ) -> Path:
        """Run verified native neural 4X and bicubic-adjust to pre-SeedVR2 factor."""
        model = model_override or ("BasicVSRPlusPlus_x4" if self._selected_preseed_mode().startswith("BasicVSR++") else "RealBasicVSR_x4")
        if model not in ("RealBasicVSR_x4", "BasicVSRPlusPlus_x4"):
            raise BackendError(f"Unsupported temporal neural SR model: {model}. Use a native 4X checkpoint.")
        if int(scale) != 4:
            raise BackendError(f"{model} requires native 4X, not {scale}X.")
        _native_start = self._job_elapsed_now(job)

        python_text = str(self._job_setting("native_sr_python", self.native_sr_python)).strip().strip('"')
        # Resolve paths for each chosen neural model independently. A user-supplied
        # override applies only when it explicitly belongs to the chosen model.
        if model == "BasicVSRPlusPlus_x4":
            default_base = Path(r"C:\Upscaler\BasicVSR_PP")
            default_cfg = default_base / "configs" / "basicvsr_plusplus_reds4.py"
            default_ckpt = default_base / "checkpoints" / "basicvsr_plusplus_reds4.pth"
        else:
            default_base = Path(r"C:\Upscaler\RealBasicVSR")
            default_cfg = default_base / "configs" / "realbasicvsr_x4.py"
            default_ckpt = default_base / "checkpoints" / "RealBasicVSR_x4.pth"
        configured_model = str(self._job_setting("native_sr_model", self.native_sr_model))
        if configured_model == model:
            repo = Path(str(self._job_setting("native_sr_repo", self.native_sr_repo)).strip().strip('"'))
            config = Path(str(self._job_setting("native_sr_config", self.native_sr_config)).strip().strip('"'))
            checkpoint = Path(str(self._job_setting("native_sr_checkpoint", self.native_sr_checkpoint)).strip().strip('"'))
        else:
            repo, config, checkpoint = default_base, default_cfg, default_ckpt
        max_seq_raw = str(self._job_setting("native_sr_max_seq_len", self.native_sr_max_seq_len)).strip()
        try:
            chunk_frames = int(self._job_setting("native_sr_chunk_frames", self.native_sr_chunk_frames))
        except Exception:
            raise BackendError("Neural SR frames-per-chunk must be an integer.")
        if not 1 <= chunk_frames <= 120:
            raise BackendError("Neural SR frames-per-chunk must be between 1 and 120.")

        python_cmd = python_text or "python"
        if any(ch in python_cmd for ch in ('\\', '/', ':')) and not Path(python_cmd).is_file():
            raise BackendError(f"RealBasicVSR Python executable was not found: {python_cmd}")
        if not repo.is_dir():
            raise BackendError(f"RealBasicVSR repository folder was not found: {repo}")
        script = repo / ("demo/restoration_video_demo.py" if model.startswith("BasicVSRPlusPlus_") else "inference_realbasicvsr.py")
        if not script.is_file():
            raise BackendError(f"{model} inference script was not found: {script}")
        if not config.is_file():
            raise BackendError(f"{model} config file was not found: {config}")
        if not checkpoint.is_file():
            raise BackendError(f"{model} checkpoint file was not found: {checkpoint}")

        max_seq: Optional[int]
        if max_seq_raw.lower() in ("", "none", "auto", "0"):
            max_seq = None
        else:
            try:
                max_seq = int(max_seq_raw)
            except Exception:
                raise BackendError("Neural SR max_seq_len must be None/Auto/0 or an integer.")
            if max_seq < 1:
                raise BackendError("Neural SR max_seq_len must be positive.")

        if self.comfy_proc is not None and self.comfy_proc.poll() is None:
            self._stop_managed_comfy(
                reason=f"V246 VRAM RESERVATION: stopping owned ComfyUI before {model} "
                       "to release dedicated GPU memory; SeedVR2 relaunches on demand.",
                wait_port=True,
            )

        input_info = self._probe_video(source)
        if input_info.width <= 0 or input_info.height <= 0 or input_info.fps <= 0:
            raise BackendError("Cannot determine source resolution or frame rate for RealBasicVSR.")
        out_w, out_h = input_info.width * scale, input_info.height * scale
        target_factor = float(scale if requested_factor is None else requested_factor)
        if not math.isfinite(target_factor) or not 0.05 <= target_factor <= 10.0:
            raise BackendError("Temporal neural SR final factor must be between 0.05X and 10X.")
        final_w = self._even_dimension(input_info.width * target_factor)
        final_h = self._even_dimension(input_info.height * target_factor)
        needs_bicubic = (final_w, final_h) != (out_w, out_h)
        if model_override is not None and needs_bicubic:
            raise BackendError("Neural scaling stage requires native 4X, without post-neural bicubic scaling.")
        if max(out_w, out_h, final_w, final_h) > 8192:
            raise BackendError("Neural or bicubic SR output would exceed 8192px; target rejected for legacy SeedVR2.")
        self._post("log", f"V240 PRE-SEEDVR2 SCALE PLAN: source={input_info.width}x{input_info.height}; "
                          f"native {scale}X={out_w}x{out_h}; requested={target_factor:g}X -> "
                          f"{final_w}x{final_h}; "
                          + (f"bicubic {target_factor/scale:g}X {'upscale' if target_factor > scale else 'downscale'} after neural SR"
                             if needs_bicubic else "no bicubic stage")
                          + "; SeedVR2 stage has its own independent preset/custom factor.")

        fps = Fraction(float(input_info.fps)).limit_denominator(100100)
        fps_text = f"{fps.numerator}/{fps.denominator}"
        if model == "BasicVSRPlusPlus_x4":
            if needs_bicubic:
                raise BackendError("BasicVSR++ scaling is exactly native 4X; separate Bicubic stage for other factors.")
            return self._run_basicvsr_ram_stream(
                job, source, temp_dir, python_cmd, config, checkpoint,
                max_seq, chunk_frames, input_info, out_w, out_h)
        base = Path(temp_dir) / f"V225_{model}_neuralSR"
        src_dir = base / "png_in"
        dst_dir = base / "png_out"
        seg_dir = base / "lossless_segments"
        for folder in (src_dir, dst_dir, seg_dir):
            folder.mkdir(parents=True, exist_ok=True)
        log_file = base / "ffmpeg_decoder_errors.txt"
        self._post("log", f"V225 {model} START: {input_info.width}x{input_info.height} -> {out_w}x{out_h}; chunk={chunk_frames}; max_seq_len={max_seq if max_seq is not None else 'None'}; PNG decode -> neural SR -> lossless FFV1; no wrapper interpolation.")
        cmd = [self._tool(self.ffmpeg.get()), "-hide_banner", "-loglevel", "error", "-i", str(source), "-map", "0:v:0", "-an", "-sn", "-pix_fmt", "rgb24", "-c:v", "png", "-f", "image2pipe", "pipe:1"]
        self._post("log", "V224 SR decoder (streamed, no full-movie PNG extraction): " + self._quote(cmd))
        segments = []
        total = 0
        job.native_vsr_frames_expected = max(
            1, int(input_info.frames or round(input_info.duration * input_info.fps) or 1)
        )
        job.native_vsr_frames_done = 0
        job.native_vsr_stage_eta_seconds = None
        decoder = None
        with log_file.open("wb") as err:
            try:
                decoder = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=err, bufsize=0, creationflags=self._no_window())
                assert decoder.stdout is not None
                while True:
                    self._wait_if_paused()
                    if self.stop_event.is_set():
                        raise Cancelled()
                    names = []
                    for idx in range(chunk_frames):
                        if self.stop_event.is_set():
                            raise Cancelled()
                        png = self._native_sr_read_png(decoder.stdout)
                        if png is None:
                            break
                        name = f"frame_{idx:08d}.png"
                        (src_dir / name).write_bytes(png)
                        names.append(name)
                    if not names:
                        break

                    for path in dst_dir.glob('*'):
                        if path.is_file():
                            path.unlink(missing_ok=True)

                    sr_cmd = [python_cmd, str(script), str(config), str(checkpoint),
                              str(src_dir), str(dst_dir)]
                    if max_seq is not None:
                        sr_cmd.extend(["--max_seq_len", str(max_seq)])
                    native_errors: List[str] = []
                    rc = self._run_process(sr_cmd, job, error_capture=native_errors)
                    if rc != 0:
                        raise BackendError(f"{model} exited with code {rc}. See live log; native neural 4X required.")

                    for name in names:
                        target = dst_dir / name
                        if not target.is_file() or target.stat().st_size < 64:
                            raise BackendError(f"{model} output frame missing: {target}")
                        w, h = self._native_sr_png_size(target)
                        if (w, h) != (out_w, out_h):
                            raise BackendError(f"{model} produced {w}x{h}, expected native {out_w}x{out_h}. The output is rejected to avoid hidden resize.")

                    segment = seg_dir / f"segment_{len(segments):05d}.mkv"
                    encode = [self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "error", "-framerate", fps_text, "-start_number", "0", "-i", str(dst_dir / "frame_%08d.png"), "-frames:v", str(len(names)), "-an", "-c:v", "ffv1", "-level", "3", "-pix_fmt", "gbrp", str(segment)]
                    if self._run_process(encode, job) != 0 or not segment.is_file() or segment.stat().st_size < 1024:
                        raise BackendError(f"FFmpeg could not encode {model} lossless segment {segment.name}.")
                    segments.append(segment)
                    total += len(names)
                    job.native_vsr_frames_done = total
                    expected = max(1, job.native_vsr_frames_expected)
                    fraction = min(1.0, total / expected)
                    elapsed_vsr = max(0.001, self._job_elapsed_now(job) - _native_start)
                    job.native_vsr_eta_reference_elapsed = self._job_elapsed_now(job)
                    if total > 0 and total < expected:
                        job.native_vsr_stage_eta_seconds = max(
                            0.0, elapsed_vsr / total * (expected - total)
                        )
                    else:
                        job.native_vsr_stage_eta_seconds = 0.0

                    self._set_stage_fraction(job, 0.68 * fraction)
                    self._post(
                        "step",
                        f"Current step: {model} native 4X: {total}/{expected} frames "
                        f"({fraction * 100:.0f}%) | neural ETA "
                        f"{self._fmt_time(job.native_vsr_stage_eta_seconds)}",
                    )
                    self._post("log", f"V246 {model}: {total}/{expected} frame(s) completed "
                                      f"({fraction*100:.0f}%); neural stage ETA "
                                      f"{self._fmt_time(job.native_vsr_stage_eta_seconds)}; "
                                      f"native {scale}X verified at {out_w}x{out_h}.")
                    for name in names:
                        (src_dir / name).unlink(missing_ok=True)
                        (dst_dir / name).unlink(missing_ok=True)
                decoder.stdout.close()
                result = decoder.wait(timeout=120)
                if result != 0:
                    raise BackendError(f"FFmpeg RealBasicVSR decode failed (code {result}). See {log_file}.")
            finally:
                if decoder is not None:
                    if decoder.poll() is None:
                        try:
                            decoder.terminate()
                            decoder.wait(timeout=3)
                        except Exception:
                            decoder.kill()
                    if decoder.stdout is not None and not decoder.stdout.closed:
                        decoder.stdout.close()
        if not segments:
            raise BackendError(f"No frames were decoded for {model} super-resolution.")
        output = base / f"{model}_{scale}X_lossless.mkv"
        if len(segments) == 1:
            shutil.copy2(segments[0], output)
        else:
            concat_file = base / "concat_segments.ffconcat"
            with concat_file.open("w", encoding="utf-8") as fh:
                fh.write("ffconcat version 1.0\n")
                for segment in segments:
                    fh.write("file '" + segment.as_posix().replace("'", "'\\''") + "'\n")
            join = [self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "error", "-safe", "0", "-f", "concat", "-i", str(concat_file), "-c", "copy", str(output)]
            if self._run_process(join, job) != 0:
                raise BackendError(f"Could not join lossless {model} output chunks.")
        verify = self._probe_video(output)
        if (verify.width, verify.height) != (out_w, out_h):
            raise BackendError(f"{model} lossless video has invalid geometry {verify.width}x{verify.height} instead of {out_w}x{out_h}.")
        if verify.frames and abs(verify.frames - total) > 1:
            raise BackendError(f"{model} output frame count {verify.frames} != decoded source frames {total}.")
        self._post("log", f"V240 {model} NATIVE {scale}X DONE: {total} frames at {out_w}x{out_h}; video={output}. "
                          "Any selected bicubic completion runs next; the SeedVR2 factor is configured independently.")

        job.stage_native_vsr_seconds += max(0.0, self._job_elapsed_now(job) - _native_start)
        job.native_vsr_stage_eta_seconds = 0.0
        self._set_stage_fraction(job, 0.69)
        if needs_bicubic:
            _bicubic_start = self._job_elapsed_now(job)
            bicubic_out = base / f"{model}_native4X_bicubic_to_{target_factor:g}X_lossless.mkv"
            bicubic_cmd = [
                self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(output), "-map", "0:v:0", "-an", "-sn",
                "-vf", f"scale={final_w}:{final_h}:flags=bicubic,format=gbrp",
                "-c:v", "ffv1", "-level", "3", "-pix_fmt", "gbrp",
                "-fps_mode", "passthrough", str(bicubic_out),
            ]
            self._post("log", "V240 BICUBIC PRE-SEEDVR2: " + self._quote(bicubic_cmd))
            if self._run_process(bicubic_cmd, job) != 0 or not bicubic_out.is_file() or bicubic_out.stat().st_size < 1024:
                raise BackendError("Post-VSR bicubic completion failed; SeedVR2 was not started.")
            resized_info = self._probe_video(bicubic_out)
            if (resized_info.width, resized_info.height) != (final_w, final_h):
                raise BackendError(f"Bicubic output geometry mismatch: got "
                                   f"{resized_info.width}x{resized_info.height}, expected {final_w}x{final_h}.")
            if resized_info.frames and abs(resized_info.frames - total) > 1:
                raise BackendError(f"Bicubic completion changed frame count: {resized_info.frames} vs {total}.")
            if abs(resized_info.fps - input_info.fps) > 0.02:
                raise BackendError(f"Bicubic completion changed FPS: {resized_info.fps} vs {input_info.fps}.")
            output = bicubic_out
            job.stage_preseed_resize_seconds = max(0.0, self._job_elapsed_now(job) - _bicubic_start)
            self._post("log", f"V240 BICUBIC PRE-SEEDVR2 VERIFIED: final={final_w}x{final_h} "
                              f"({target_factor:g}X overall); {total} frames; "
                              "SeedVR2 subsequently uses the selected preset/custom multiplier.")
        for segment in segments:
            segment.unlink(missing_ok=True)
        self._set_stage_fraction(job, 0.70)
        return output

    def _run_seedvr2(self, job: Job, src: Path, factor: float, temp_dir: Path) -> Path:
        ai_ref = job.ai_info or job.info
        manual_batch, manual_overlap, _tile, _spatial = self._seed_user_controls(job)
        batch, overlap = self._auto_seed_temporal_params(ai_ref, factor, manual_batch)
        if manual_overlap is not None:
            overlap = manual_overlap
        if overlap >= batch:
            raise BackendError(f"SeedVR2 overlap {overlap} cannot equal/exceed batch {batch}.")

        if not job.seed_benchmark_run_id:
            job.seed_benchmark_run_id = uuid.uuid4().hex
        if not job.seed_initial_batch_requested:
            job.seed_initial_batch_requested = ("Auto (resolution-dependent)" if
                str(self._job_setting("seed_parameter_mode", self.seed_parameter_mode)) == SEED_PARAMETER_MODES[0]
                else str(self._job_setting("seed_batch_max", self.seed_batch_max)).strip() or "Auto")
            job.seed_initial_overlap_requested = str(manual_overlap if manual_overlap is not None else "Auto")
            job.seed_initial_vae_tile_requested = str(_tile)
            job.seed_initial_vae_overlap_requested = str(_spatial if _spatial is not None else "Auto")

        attempt = 1
        while True:
            self._seed_spill_trigger = False
            self._spill_consecutive = 0
            self._seed_batch_times = []
            self._seed_last_prompt_seconds = 0.0
            self._seed_last_meta_batch = 0
            if attempt == 1:
                self._post("log", f"V256 EFFECTIVE SEEDVR2: mode={self._job_setting('seed_parameter_mode', self.seed_parameter_mode)}; "
                           f"AI source={ai_ref.width}x{ai_ref.height}; requested scale={factor:g}X; "
                           f"frames/batch={batch}; temporal overlap={overlap}; "
                           f"VAE tile={_tile}; spatial overlap={_spatial}")
            self._post("log", f"SeedVR2 attempt {attempt}: frames/batch={batch}, overlap={overlap}")
            if attempt == 1:
                self._post(
                    "log",
                    "VRAM SAFETY V62: Shared GPU memory is monitored for the user but does NOT reduce the batch. "
                    "Automatic backoff occurs only after an actual CUDA/ComfyUI memory-allocation failure."
                )
            job.seed_attempt_count += 1
            attempt_started = time.perf_counter()
            attempted_batch, attempted_overlap = batch, overlap
            status, failure_text = "FAILED", ""
            gpu_done, gpu_thread, gpu_sample = self._seed_start_benchmark_sampler()
            try:
                result = self._run_seedvr2_attempt(job, src, factor, temp_dir, attempted_batch)
                status = "SUCCESS"
            except VramSpillDetected as exc:
                job.seed_oom_retry_count += 1
                status = ("OOM_FAILED" if attempted_batch <= 5 or attempt >= 6 else "OOM_RETRY")
                failure_text = str(exc)
            except Cancelled as exc:
                status, failure_text = "CANCELLED", str(exc)
                raise
            except Exception as exc:
                status, failure_text = "FAILED", str(exc)
                raise
            finally:
                # Stop timing before doing potentially lengthy backoff/relaunch work.
                elapsed = max(0.000001, time.perf_counter() - attempt_started)
                gpu_done.set()
                gpu_thread.join(timeout=3.5)
                self._record_seed_benchmark_attempt(
                    job, attempt, attempted_batch, attempted_overlap, factor,
                    elapsed, status, failure_text, gpu_sample,
                )

            if status == "SUCCESS":
                return result
            if attempted_batch <= 5:
                raise BackendError(
                    "SeedVR2 produced a real GPU memory-allocation failure even at the minimum "
                    "5-frame temporal batch. Reduce the requested upscale/output resolution."
                )
            if attempt >= 6:
                raise BackendError("SeedVR2 could not find a stable temporal batch after multiple genuine OOM retries.")
            safer = self._next_safer_seed_batch(attempted_batch)
            self._post(
                "log", f"VRAM SAFETY: actual allocation/OOM failure at frames/batch={attempted_batch}. "
                f"Reducing {attempted_batch} -> {safer} and restarting hidden ComfyUI before retry."
            )
            self._interrupt_comfy_prompt()
            self._stop_managed_comfy(
                reason="VRAM SAFETY: stopping V62-owned ComfyUI before retry.",
                wait_port=True,
            )
            self._post("comfy_status", "Hidden ComfyUI: restarting after real VRAM allocation failure")
            self._wait_for_gpu_release(15.0)
            batch = safer
            _, overlap = self._auto_seed_temporal_params(ai_ref, factor, batch)
            if manual_overlap is not None:
                overlap = manual_overlap
            if overlap >= batch:
                raise BackendError("SeedVR2 overlap is too large for the OOM-reduced batch. Lower temporal overlap.")
            attempt += 1

    def _run_seedvr2_attempt(self, job: Job, src: Path, factor: float, temp_dir: Path, batch_override: int) -> Path:
        self._ensure_hidden_comfy()
        ai_ref = job.ai_info or job.info
        auto_batch, auto_overlap = self._auto_seed_temporal_params(ai_ref, factor, batch_override)
        _user_batch, manual_overlap, _tile, _spatial = self._seed_user_controls(job)
        selected_overlap = int(manual_overlap if manual_overlap is not None else auto_overlap)
        expected_batches = int(math.ceil(ai_ref.frames / max(1, auto_batch))) if ai_ref.frames else 0
        out_w = int(round(ai_ref.width * factor)) if ai_ref.width else 0
        out_h = int(round(ai_ref.height * factor)) if ai_ref.height else 0
        expected_w = self._even_dimension(ai_ref.width * float(factor))
        expected_h = self._even_dimension(ai_ref.height * float(factor))

        job.seed_batch_used = int(auto_batch)
        job.seed_overlap_used = int(selected_overlap)
        job.seed_expected_batches = int(expected_batches or 0)
        benchmark_pixels = SEED_REF_OUT_PIXELS
        workload_ratio = ((out_w * out_h) / benchmark_pixels) if out_w and out_h else 0.0

        self._post(
            "log",
            f"SeedVR2 PREPLAN V62: source={ai_ref.width}x{ai_ref.height}@{ai_ref.fps:.3f}fps; requested scale={factor}X; "
            f"AI output~{out_w}x{out_h}; reference=1536x960 @ 49 frames; "
            f"selected frames/batch={auto_batch}; overlap={selected_overlap}; expected Meta-Batches={expected_batches or '?'}"
        )
        self._post(
            "log",
            f"SeedVR2 plan: source={ai_ref.width}x{ai_ref.height}@{ai_ref.fps:.3f}fps, scale={factor}X, "
            f"AI output~{out_w}x{out_h}, frames={ai_ref.frames or '?'}; "
            f"frames/batch={auto_batch}, overlap={selected_overlap}, "
            f"expected Meta-Batches={expected_batches or '?'}; launcher={self._job_setting("comfy_launch_mode", self.comfy_launch_mode)}. "
            f"Spatial workload is ~{workload_ratio:.2f}x the 1536x960 completed direct-ComfyUI reference."
        )

        wf, copied_input = self._prepare_api_workflow(src, factor, ai_ref, auto_batch, job=job)
        vae_nodes = [node.get("inputs", {}) for node in wf.values()
                     if "vae" in str(node.get("class_type", "")).lower()
                     and "tiled" in str(node.get("class_type", "")).lower()
                     and "tile_size" in node.get("inputs", {})]
        if vae_nodes:
            job.seed_vae_tile_used = int(vae_nodes[0].get("tile_size", 0) or 0)
            job.seed_vae_spatial_overlap_used = int(vae_nodes[0].get("overlap", 0) or 0)
            if any(int(node.get("tile_size", 0) or 0) != job.seed_vae_tile_used or
                   int(node.get("overlap", 0) or 0) != job.seed_vae_spatial_overlap_used
                   for node in vae_nodes[1:]):
                self._post("log", "V250 WARNING: tiled VAE encode/decode nodes have mismatched tile/overlap settings.")
        if copied_input is None:
            raise BackendError("SeedVR2 workflow did not create a managed ComfyUI input copy.")

        token = copied_input.name
        self._retain_comfy_input(copied_input)
        self._clear_seedvr2_token_state(token)

        self.comfy_final_event.clear()
        self.comfy_final_path = None
        self.comfy_prompt_error = ""
        self.comfy_seed_progress = 0.0

        output_root = self._comfy_runtime_output_dir
        if output_root is None:
            root = Path(self.comfy_root.get().strip())
            output_root = root / "ComfyUI" / "output"
        output_root.mkdir(parents=True, exist_ok=True)
        runtime_root = self._comfy_runtime_root or output_root.parent
        self._post(
            "temp",
            f"Temporary files: {runtime_root} (active SeedVR2 private ComfyUI runtime)"
        )
        output_before = self._snapshot_comfy_video_outputs(output_root)

        baseline = self._read_windows_shared_gpu_mib()
        if baseline is not None:
            self._shared_baseline_mib = max(0.0, float(baseline))
            self._spill_delta_mib = 0.0
            self._post(
                "log",
                f"Shared GPU baseline before SeedVR2 = "
                f"{self._shared_baseline_mib/1024.0:.2f} GB (informational only)."
            )

        self.comfy_job_active = True
        self._seed_active_batch = auto_batch
        self._seed_spill_trigger = False
        self._seed_expected_meta_batches = int(expected_batches or 0)
        self._seed_last_meta_batch = 0
        self._seed_meta_overrun = False
        start = time.time()
        pid = ""
        history_success_logged = False
        idle_without_final_since: Optional[float] = None
        idle_warning_logged = False

        token_final_seen_at: Optional[float] = None
        token_final_candidate: Optional[Path] = None
        token_final_state: Dict[str, Any] = {}

        fs_states: Dict[str, Dict[str, Any]] = {}
        fs_logged: set = set()

        try:
            submitted_at = time.time()
            pid = self._submit_prompt(wf)
            self._post(
                "log",
                f"SeedVR2 submitted to hidden ComfyUI. prompt_id={pid}; "
                f"scale={factor}X; input_token={token}"
            )
            self._post(
                "log",
                "V255 SEEDVR2 COMPLETION LOCK: prompt history and stable output files are "
                "advisory; require the entire expected duration/frame count before accepting "
                "a token-bound or private-folder output. Intermediate MetaBatch muxes are NOT final."
            )

            while True:
                paused_for = self._wait_if_paused()
                start += paused_for
                if token_final_seen_at is not None:
                    token_final_seen_at += paused_for

                if self.stop_event.is_set():
                    self._interrupt_comfy_prompt()
                    raise Cancelled()

                proc = self.comfy_proc
                if proc is None or proc.poll() is not None:
                    raise BackendError(
                        "The V62-owned ComfyUI process exited before SeedVR2 produced a valid output."
                    )

                if self._seed_spill_trigger:
                    self._post(
                        "log",
                        f"VRAM SAFETY: genuine allocation/OOM failure with frames/batch={auto_batch}; "
                        "interrupting this attempt for a safer retry."
                    )
                    self._interrupt_comfy_prompt()
                    raise VramSpillDetected(f"GPU allocation/OOM failure with batch {auto_batch}")


                record = self._comfy_prompt_history(pid)
                if record is not None:
                    completed, history_error = self._comfy_history_state(record)
                    if history_error:
                        raise BackendError(f"SeedVR2 prompt {pid} failed: {history_error}")
                    if completed and not history_success_logged:
                        history_success_logged = True
                        self._post(
                            "log",
                            f"SeedVR2 prompt_id={pid} has an intermediate history success; "
                            "V62 continues monitoring Meta-Batch output."
                        )


                bound = self._seedvr2_final_for_token(token)
                if bound is not None:
                    if token_final_candidate is None or str(token_final_candidate) != str(bound):
                        token_final_candidate = Path(bound)
                        token_final_seen_at = time.time()
                        token_final_state.clear()
                        self._post(
                            "log",
                            f"SEEDVR2 V62 TOKEN-BOUND FINAL detected for {token}: {token_final_candidate}"
                        )

                    ready = self._probe_seedvr2_final_when_stable(
                        token_final_candidate, job, expected_w, expected_h, token_final_state, submitted_at
                    )
                    if ready is not None:
                        self._post(
                            "log",
                            f"SeedVR2 V62 FINAL VERIFIED by token: token={token}; "
                            f"output={ready}; geometry={self._probe_video(ready).width}x"
                            f"{self._probe_video(ready).height}; planned={expected_w}x{expected_h}."
                        )
                        return ready

                    if (
                        token_final_seen_at is not None
                        and time.time() - token_final_seen_at > 60.0
                    ):
                        raise BackendError(
                            f"SeedVR2 emitted a Final mux event for {token}, but the output did not "
                            f"become a stable/probeable {expected_w}x{expected_h} video within 60 seconds: "
                            f"{token_final_candidate}"
                        )


                changed = self._changed_comfy_video_outputs(
                    output_root, output_before, submitted_at
                )
                for candidate in changed:
                    key = str(candidate).lower()
                    state = fs_states.setdefault(key, {})
                    ready = self._probe_private_seedvr2_output_when_stable(
                        candidate, job, expected_w, expected_h, state
                    )
                    if ready is None:
                        continue
                    if key not in fs_logged:
                        fs_logged.add(key)
                        self._post(
                            "log",
                            f"SEEDVR2 V62 PRIVATE-OUTPUT FALLBACK: detected complete "
                            f"output within 4 pixels of {expected_w}x{expected_h} for {token}: {ready}"
                        )
                    self._post(
                        "log",
                        f"SeedVR2 V62 FINAL VERIFIED by private output folder: "
                        f"token={token}; output={ready}; "
                        f"actual={self._probe_video(ready).width}x{self._probe_video(ready).height}; "
                        f"planned={expected_w}x{expected_h}."
                    )
                    return ready

                queue_idle = self._comfy_queue_idle()

                if (
                    self._seed_expected_meta_batches > 0
                    and self._seed_last_meta_batch > self._seed_expected_meta_batches
                ):
                    self._post(
                        "log",
                        f"SEEDVR2 V62 SAFETY STOP: observed Meta-Batch "
                        f"{self._seed_last_meta_batch}/{self._seed_expected_meta_batches} for {token}; "
                        f"expected processing should have ended at "
                        f"{self._seed_expected_meta_batches}/{self._seed_expected_meta_batches}. "
                        "Interrupting this runaway attempt to prevent unnecessary extra processing."
                    )
                    self._interrupt_comfy_prompt()
                    raise BackendError(
                        f"SeedVR2 exceeded expected Meta-Batches "
                        f"({self._seed_last_meta_batch}/{self._seed_expected_meta_batches}) "
                        f"without producing a valid completed output. The attempt was stopped "
                        f"to prevent over-processing."
                    )

                if self.comfy_prompt_error and queue_idle and token_final_candidate is None:
                    raise BackendError(
                        f"SeedVR2 processing stopped without a valid output for {token}: "
                        f"{self.comfy_prompt_error}"
                    )


                if history_success_logged and token_final_candidate is None and queue_idle:
                    if idle_without_final_since is None:
                        idle_without_final_since = time.time()
                    elif (
                        time.time() - idle_without_final_since > 180.0
                        and not idle_warning_logged
                    ):
                        idle_warning_logged = True
                        self._post(
                            "log",
                            f"SEEDVR2 V62 WARNING: queue has been idle for 180 seconds after an "
                            f"intermediate history success for {token}. V62 will NOT falsely fail "
                            "the video; it keeps watching the private output folder and token-bound final event."
                        )
                else:
                    idle_without_final_since = None
                    idle_warning_logged = False

                if self.comfy_seed_progress <= 0:
                    elapsed = time.time() - start
                    pseudo = min(
                        0.15,
                        elapsed / max(300.0, job.info.duration * 30.0) * 0.15
                    )
                    self._post("seed_progress", pseudo)

                time.sleep(0.5)
        finally:
            self.comfy_job_active = False


    def _comfy_queue_idle(self) -> bool:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{self._comfy_api_port()}/queue", timeout=2) as r:
                q = json.loads(r.read().decode("utf-8"))
            return not q.get("queue_running") and not q.get("queue_pending")
        except Exception:
            return False

    def _interrupt_comfy_prompt(self):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{self._comfy_api_port()}/interrupt", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=2).read()
        except Exception:
            pass

    def _vapoursynth_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        plugin_dirs = []
        raw = self.rife_plugin_dir.get().strip()
        if not raw and self.rife_plugin_dll.get().strip():
            raw = str(Path(self.rife_plugin_dll.get().strip()).parent)
        if raw:
            p = Path(raw)
            if p.is_dir():
                plugin_dirs.append(str(p))
        source_dll = self.vs_source_plugin_dll.get().strip()
        if source_dll:
            p = Path(source_dll).parent
            if p.is_dir() and str(p) not in plugin_dirs:
                plugin_dirs.append(str(p))
        previous = env.get("VAPOURSYNTH_EXTRA_PLUGIN_PATH", "").strip()
        if previous:
            plugin_dirs.append(previous)
        if plugin_dirs:
            env["VAPOURSYNTH_EXTRA_PLUGIN_PATH"] = os.pathsep.join(plugin_dirs)
            env["PATH"] = os.pathsep.join(plugin_dirs) + os.pathsep + env.get("PATH", "")
        return env


    def _verified_output_geometry(self, job: Job, actual: VideoInfo, context: str) -> Tuple[int, int]:
        expected_w, expected_h, _fps, _scale = self._output_geometry(job.info)
        if min(actual.width, actual.height) < 2:
            raise BackendError(f"{context}: invalid output dimensions.")
        if abs(actual.width - expected_w) > 4 or abs(actual.height - expected_h) > 4:
            raise BackendError(f"{context}: output {actual.width}x{actual.height} does not match requested {expected_w}x{expected_h}. No implicit resize is permitted.")
        job.verified_ai_output_width = int(actual.width)
        job.verified_ai_output_height = int(actual.height)
        return int(actual.width), int(actual.height)


    def _rife_border_protection_plan(
        self,
        info: VideoInfo,
    ) -> Tuple[int, int, int, int, bool]:
        w = max(1, int(info.width or 0))
        h = max(1, int(info.height or 0))

        base = 32
        left = base
        right = base
        top = base
        bottom = base


        align = 64
        protected_w = w + left + right
        protected_h = h + top + bottom

        right += (align - (protected_w % align)) % align
        bottom += (align - (protected_h % align)) % align


        use_uhd = bool(
            w >= 1280
            or h >= 720
            or (w * h) >= 900_000
        )

        return left, right, top, bottom, use_uhd

    def _rife_and_encode(self, job: Job, seed_video: Path, audio_source: Path, final_root: Path, temp_dir: Path, extra_video_filters: Optional[List[str]] = None) -> Path:
        self._wait_if_paused()

        seed_video = Path(seed_video)
        if not seed_video.is_file():
            raise BackendError(
                f"RIFE input does not exist before pipeline start: {seed_video}. "
                f"This indicates an upstream output-lifetime error."
            )
        known_seed_info = None
        for candidate in (job.ai_info, job.info):
            if candidate is not None and self._same_video_path(seed_video, Path(candidate.path)):
                known_seed_info = candidate
                break
        try:
            self._probe_video_resilient(
                seed_video,
                fallback=known_seed_info,
                context="RIFE input",
            )
        except Exception as e:
            raise BackendError(
                f"RIFE input exists but cannot be probed before pipeline start: "
                f"{seed_video}: {e}"
            )

        vspipe = self._tool(self.vspipe.get())
        vpy = temp_dir / "rife_in_memory.vpy"
        src_literal = repr(str(seed_video))
        matrix = "709" if job.info.height > 576 else "470bg"
        rife_dll_literal = repr(self.rife_plugin_dll.get().strip())
        source_dll_literal = repr(self.vs_source_plugin_dll.get().strip())
        model_path_literal = repr(self.rife_model_path.get().strip())

        ai_info = self._probe_video_resilient(
            seed_video,
            fallback=known_seed_info,
            context="RIFE input",
        )
        use_rife, rife_factor, planned_rife_fps = self._rife_plan_for_fps(ai_info.fps)
        if not use_rife:
            raise BackendError("RIFE was invoked even though the current RIFE plan does not require interpolation.")

        mode = self._selected_rife_mode()
        if mode == "Target FPS":
            target_fraction = Fraction(str(planned_rife_fps)).limit_denominator(100000)
            target_num = int(target_fraction.numerator)
            target_den = int(target_fraction.denominator)
            self._post(
                "log",
                f"V141 RIFE exact-target plan: input={ai_info.fps:.6g} FPS; "
                f"target={planned_rife_fps:.6g} FPS; native RIFE fps_num={target_num}, fps_den={target_den}. "
                f"No 75 FPS intermediate and no FFmpeg frame dropping are used."
            )
        else:
            target_num = 0
            target_den = 1
            self._post(
                "log",
                f"V141 RIFE multiplier plan: input={ai_info.fps:.6g} FPS × {rife_factor} = {planned_rife_fps:.6g} FPS."
            )

        (
            pad_left,
            pad_right,
            pad_top,
            pad_bottom,
            rife_uhd,
        ) = self._rife_border_protection_plan(ai_info)

        padded_w = int(ai_info.width + pad_left + pad_right)
        padded_h = int(ai_info.height + pad_top + pad_bottom)

        self._post(
            "log",
            f"V141 RIFE seam protection: replicated-edge padding "
            f"L{pad_left}/R{pad_right}/T{pad_top}/B{pad_bottom}; "
            f"{ai_info.width}x{ai_info.height} -> {padded_w}x{padded_h}; "
            f"native UHD={'ON' if rife_uhd else 'OFF'}; "
            f"crop returns exactly to {ai_info.width}x{ai_info.height}."
        )

        uhd_literal = "True" if rife_uhd else "False"

        model_path = self.rife_model_path.get().strip()
        if not model_path:
            raise BackendError("RIFE model folder is required. Use the contained RIFE model folder with flownet.param and flownet.bin.")
        if not (Path(model_path) / "flownet.param").is_file() or not (Path(model_path) / "flownet.bin").is_file():
            raise BackendError(
                f"RIFE model folder is incomplete: {model_path}. Expected flownet.param and flownet.bin."
            )

        if mode == "Target FPS":
            rife_call = (
                f"rgb_rife = core.rife.RIFE(rgb_pad, model_path={model_path_literal}, "
                f"fps_num={target_num}, fps_den={target_den}, gpu_id=0, "
                f"gpu_thread={RIFE_GPU_THREADS_FIXED}, uhd={uhd_literal})"
            )
        else:
            rife_call = (
                f"rgb_rife = core.rife.RIFE(rgb_pad, model_path={model_path_literal}, "
                f"factor_num={int(rife_factor)}, factor_den=1, gpu_id=0, "
                f"gpu_thread={RIFE_GPU_THREADS_FIXED}, uhd={uhd_literal})"
            )

        script = f"""import vapoursynth as vs
core = vs.core
_rife_dll = {rife_dll_literal}
_source_dll = {source_dll_literal}
if _rife_dll and not hasattr(core, "rife"):
    core.std.LoadPlugin(path=_rife_dll)
if _source_dll and not (hasattr(core, "bs") or hasattr(core, "lsmas") or hasattr(core, "ffms2")):
    core.std.LoadPlugin(path=_source_dll)
src = {src_literal}
if hasattr(core, "bs"):
    clip = core.bs.VideoSource(src)
elif hasattr(core, "lsmas"):
    clip = core.lsmas.LWLibavSource(src)
elif hasattr(core, "ffms2"):
    clip = core.ffms2.Source(src)
else:
    raise RuntimeError("RIFE requires VapourSynth BestSource (core.bs), L-SMASH-Works (core.lsmas), or FFMS2 (core.ffms2) for video input")
if not hasattr(core, "rife"):
    raise RuntimeError("VapourSynth-RIFE-ncnn-Vulkan plugin is not installed (core.rife missing)")
orig_w = clip.width
orig_h = clip.height
rgb = core.resize.Bicubic(clip, format=vs.RGBS, matrix_in_s="{matrix}")
left_edge = core.std.CropAbs(rgb, width=1, height=orig_h, left=0, top=0)
right_edge = core.std.CropAbs(rgb, width=1, height=orig_h, left=orig_w - 1, top=0)
left_pad = core.resize.Point(left_edge, width={pad_left}, height=orig_h)
right_pad = core.resize.Point(right_edge, width={pad_right}, height=orig_h)
middle = core.std.StackHorizontal([left_pad, rgb, right_pad])
middle_w = middle.width
top_edge = core.std.CropAbs(middle, width=middle_w, height=1, left=0, top=0)
bottom_edge = core.std.CropAbs(middle, width=middle_w, height=1, left=0, top=orig_h - 1)
top_pad = core.resize.Point(top_edge, width=middle_w, height={pad_top})
bottom_pad = core.resize.Point(bottom_edge, width=middle_w, height={pad_bottom})
rgb_pad = core.std.StackVertical([top_pad, middle, bottom_pad])
{rife_call}
rgb_crop = core.std.CropAbs(
    rgb_rife,
    width=orig_w,
    height=orig_h,
    left={pad_left},
    top={pad_top},
)
out = core.resize.Bicubic(
    rgb_crop,
    format=vs.YUV420P10,
    matrix_s="{matrix}",
)
out.set_output()
"""
        vpy.write_text(script, encoding="utf-8")

        env = self._vapoursynth_env()
        self._post("log", "V141 RIFE preflight: testing the RIFE DLL/model on a synthetic 64x64 clip; the real movie is not opened during preflight.")
        preflight_ok, preflight_detail = self._vapoursynth_probe(execute_rife=True)
        if not preflight_ok:
            raise BackendError(f"RIFE synthetic preflight failed. {preflight_detail}")
        self._post("log", "V141 RIFE synthetic preflight passed. " + preflight_detail)
        self._post("log", "V141 RIFE source initialization: opening the real movie now. The VapourSynth source plugin may index a long MKV before the first interpolated frame appears; this is source initialization, not RIFE GPU processing.")

        w, h = self._verified_output_geometry(job, ai_info, "RIFE input")
        fps_out = float(planned_rife_fps if planned_rife_fps and planned_rife_fps > 0 else ai_info.fps)
        if fps_out <= 0:
            raise BackendError(
                f"RIFE final output FPS could not be resolved to a positive value. "
                f"Input FPS={ai_info.fps:.6g}, planned RIFE FPS={planned_rife_fps:.6g}."
            )
        final = self._final_output_path(job, final_root, actual_geometry=(w, h))
        ffargs = self._video_encode_args(w, h, fps_out)
        scale_args = []
        audio_args = self._audio_map_args(audio_source, final.suffix.lower())
        authoritative_video_duration = float(ai_info.duration or job.info.duration or 0.0)
        if authoritative_video_duration > 0:
            for i, value in enumerate(audio_args):
                if value == "aresample=async=1000:first_pts=0":
                    audio_args[i] = "aresample=async=1000:first_pts=0,apad"
                    break

        video_filters: List[str] = []
        if len(scale_args) >= 2 and scale_args[0] == "-vf":
            video_filters.append(str(scale_args[1]))
        if extra_video_filters:
            video_filters.extend([str(x) for x in extra_video_filters if str(x).strip()])
        filter_args = ["-vf", ",".join(video_filters)] if video_filters else []

        vsp_cmd = [vspipe, "-c", "y4m", str(vpy), "-"]
        ff_cmd = [
            self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "warning",
            "-i", "pipe:0", "-i", str(audio_source), "-map", "0:v:0"
        ] + audio_args + filter_args + ffargs + [
            "-fps_mode:v", "cfr", "-max_interleave_delta", "0"
        ]
        if authoritative_video_duration > 0:
            ff_cmd += ["-t", f"{authoritative_video_duration:.6f}"]
            self._post(
                "log",
                f"V150 RIFE A/V duration protection: processed video is authoritative at "
                f"{authoritative_video_duration:.3f}s; source audio is resampled and padded with silence if "
                f"it ends early, then trimmed at the processed-video duration. FFmpeg -shortest is not used."
            )
        ff_cmd += ["-progress", "pipe:1", "-nostats", str(final)]

        self._rife_runtime_active = True
        self._rife_runtime_output_fps = 0.0
        self._rife_runtime_gpu_thread = int(
            RIFE_GPU_THREADS_FIXED
        )
        self._rife_runtime_gpu_name = self._read_nvidia_gpu_name()

        start_stats = self._read_nvidia_stats()
        if start_stats is not None:
            start_gpu, start_used_mib, start_total_mib = start_stats
            start_vram = (
                f"{start_used_mib / 1024.0:.1f}/{start_total_mib / 1024.0:.1f} GB"
                if start_total_mib > 0
                else "--"
            )
            self._post(
                "log",
                f"V141 RIFE GPU runtime: GPU={self._rife_runtime_gpu_name}; "
                f"backend=ncnn-Vulkan; device=0; GPU threads={self._rife_runtime_gpu_thread}; "
                f"GPU utilization={start_gpu:.0f}%; VRAM={start_vram}."
            )
        else:
            self._post(
                "log",
                f"V141 RIFE GPU runtime: GPU={self._rife_runtime_gpu_name}; "
                f"backend=ncnn-Vulkan; device=0; GPU threads={self._rife_runtime_gpu_thread}; "
                "NVIDIA utilization/VRAM telemetry unavailable."
            )

        self._post(
            "rife_status",
            f"RIFE GPU: {self._rife_runtime_gpu_name} | ncnn-Vulkan | device 0 | "
            f"threads {self._rife_runtime_gpu_thread} | starting..."
        )
        self._post("log", "V141 RIFE in-memory pipeline:\n" + self._quote(vsp_cmd) + " | " + self._quote(ff_cmd))
        flags = self._no_window()
        vsp = subprocess.Popen(
            vsp_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=flags,
            env=env,
        )
        with self.process_lock:
            self._aux_processes.append(vsp)
        assert vsp.stdout is not None

        vsp_stderr_lines: List[str] = []
        vsp_stderr_lock = threading.Lock()

        def drain_vsp_stderr() -> None:
            if vsp.stderr is None:
                return
            while True:
                raw = vsp.stderr.readline()
                if not raw:
                    break
                if isinstance(raw, bytes):
                    line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                else:
                    line = str(raw).rstrip("\r\n")
                if line:
                    with vsp_stderr_lock:
                        vsp_stderr_lines.append(line)
                        if len(vsp_stderr_lines) > 200:
                            del vsp_stderr_lines[:-200]
                    self._post("log", "RIFE: " + line)

        vsp_stderr_thread = threading.Thread(target=drain_vsp_stderr, daemon=True)
        vsp_stderr_thread.start()

        ff = subprocess.Popen(
            ff_cmd,
            stdin=vsp.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            creationflags=flags,
        )
        vsp.stdout.close()
        with self.process_lock:
            self.current_process = ff
        try:
            assert ff.stdout is not None
            for raw in ff.stdout:
                self._wait_if_paused()
                if self.stop_event.is_set():
                    self._terminate_tree(ff)
                    self._terminate_tree(vsp)
                    raise Cancelled()
                line = raw.strip()
                if line:
                    self._post("log", line)
                    if line.startswith("fps="):
                        try:
                            self._rife_runtime_output_fps = max(
                                0.0,
                                float(line.split("=", 1)[1].strip()),
                            )
                        except Exception:
                            pass
                    frac = self._ffmpeg_progress_fraction(line, job.info.duration)
                    if frac is not None:
                        self._set_stage_fraction(job, frac)
            rc = ff.wait()
            vsp_rc = vsp.wait()
            vsp_stderr_thread.join(timeout=2.0)
            with vsp_stderr_lock:
                err = "\n".join(vsp_stderr_lines[-80:])

            broken_pipe_signature = (
                "fwrite() call failed when writing video plane" in err
                and ("errno: 32" in err or "broken pipe" in err.lower())
            )
            recoverable_trailing_pipe_close = (
                rc == 0
                and vsp_rc != 0
                and broken_pipe_signature
            )

            if rc != 0 or (vsp_rc != 0 and not recoverable_trailing_pipe_close):
                raise BackendError(
                    f"In-memory RIFE/FFmpeg pipeline failed (vspipe={vsp_rc}, ffmpeg={rc}). "
                    f"{err[-5000:]}"
                )

            if not final.is_file() or final.stat().st_size <= 1024:
                raise BackendError(f"RIFE pipeline ended without a valid output file: {final}")

            final_info = self._probe_video(final)

            if int(final_info.width) != int(w) or int(final_info.height) != int(h):
                raise BackendError(
                    f"RIFE output verification failed: expected {w}x{h}, "
                    f"output is {final_info.width}x{final_info.height}."
                )

            if mode == "Target FPS" and abs(float(final_info.fps) - float(planned_rife_fps)) > 0.05:
                raise BackendError(
                    f"RIFE target-FPS verification failed: requested {planned_rife_fps:g} FPS, "
                    f"output is {final_info.fps:.6g} FPS."
                )

            if recoverable_trailing_pipe_close:
                expected_duration = float(ai_info.duration or job.info.duration or 0.0)
                actual_duration = float(final_info.duration or 0.0)
                duration_tolerance = max(0.50, expected_duration * 0.01) if expected_duration > 0 else 0.50

                if expected_duration > 0 and actual_duration > 0:
                    if actual_duration < expected_duration - duration_tolerance:
                        raise BackendError(
                            f"RIFE trailing broken-pipe output is too short to recover safely: "
                            f"expected about {expected_duration:.3f}s, output is {actual_duration:.3f}s "
                            f"(allowed shortfall {duration_tolerance:.3f}s)."
                        )
                    if actual_duration > expected_duration + duration_tolerance:
                        raise BackendError(
                            f"RIFE trailing broken-pipe output duration is outside the safe validation range: "
                            f"expected about {expected_duration:.3f}s, output is {actual_duration:.3f}s "
                            f"(tolerance {duration_tolerance:.3f}s)."
                        )

                self._post(
                    "log",
                    f"V141 RIFE RECOVERY: ignored trailing VSPipe broken-pipe after FFmpeg completed successfully "
                    f"(vspipe={vsp_rc}, ffmpeg={rc}). Final output passed validation: "
                    f"{final_info.width}x{final_info.height} @ {final_info.fps:.6g} FPS, "
                    f"duration={actual_duration:.3f}s. This job is treated as SUCCESS."
                )
            final_stats = self._read_nvidia_stats()
            if final_stats is not None:
                final_gpu, final_used_mib, final_total_mib = final_stats
                final_vram = (
                    f"{final_used_mib / 1024.0:.1f}/{final_total_mib / 1024.0:.1f} GB"
                    if final_total_mib > 0
                    else "--"
                )
                self._post(
                    "log",
                    f"V141 RIFE final GPU telemetry: GPU={self._rife_runtime_gpu_name}; "
                    f"backend=ncnn-Vulkan; device=0; threads={self._rife_runtime_gpu_thread}; "
                    f"GPU utilization={final_gpu:.0f}%; VRAM={final_vram}; "
                    f"throughput={self._rife_runtime_output_fps:.2f} output fps."
                )

            self._post(
                "log",
                f"V141 RIFE verified output: {final_info.width}x{final_info.height} @ "
                f"{final_info.fps:.6g} FPS; {final_info.frames or '?'} frames."
            )
            return final
        finally:
            self._rife_runtime_active = False
            self._post("rife_status", "RIFE: --")
            with self.process_lock:
                if self.current_process is ff:
                    self.current_process = None
                try:
                    self._aux_processes.remove(vsp)
                except ValueError:
                    pass

    def _final_encode(self, job: Job, video: Path, audio_source: Path, final_root: Path, extra_video_filters: Optional[List[str]] = None) -> Path:
        video = Path(video)
        if not video.is_file():
            raise BackendError(
                f"Final encoder input does not exist before encoding: {video}. "
                f"This indicates an upstream output-lifetime error."
            )
        try:
            current_info = self._probe_video(video)
        except Exception:
            current_info = None

        _planned_w, _planned_h, planned_fps, _ = self._output_geometry(job.info)
        if current_info is None:
            raise BackendError(
                f"V247 final encoder cannot verify the dimensions of its input: {video}."
            )
        w, h = self._verified_output_geometry(job, current_info, "final encoder input")
        fps = float(planned_fps if planned_fps and planned_fps > 0 else 0.0)
        if current_info is not None and current_info.fps > 0 and fps <= 0:
            fps = float(current_info.fps)
        if self._selected_rife_enable() and self._selected_rife_mode() == "Target FPS":
            selected_target = float(self._selected_rife_target_fps())
            if selected_target > 0:
                fps = selected_target
        if fps <= 0:
            raise BackendError(
                f"Final output FPS could not be resolved to a positive value for {video}."
            )

        if (self._selected_upscale_enable() and self._selected_engine() == "SeedVR2"
                and current_info is not None and current_info.width > 0 and current_info.height > 0
                and (abs(current_info.width - w) > 4 or abs(current_info.height - h) > 4)):
            raise BackendError(f"V221 AI-ONLY OUTPUT: expected native AI result {w}x{h}, got "
                               f"{current_info.width}x{current_info.height}. No FFmpeg enlargement allowed.")
        final = self._final_output_path(job, final_root, actual_geometry=(w, h))
        ffargs = self._video_encode_args(w, h, fps)
        scale_args = []
        video_filters: List[str] = []
        if len(scale_args) >= 2 and scale_args[0] == "-vf":
            video_filters.append(str(scale_args[1]))
        if extra_video_filters:
            video_filters.extend([str(x) for x in extra_video_filters if str(x).strip()])
        if (
            self._selected_rife_enable()
            and self._selected_rife_mode() == "Target FPS"
            and current_info is not None
            and current_info.fps > 0
            and abs(float(current_info.fps) - float(fps)) > 1e-6
        ):
            video_filters.append(f"fps=fps={fps:g}:round=near")
            self._post(
                "log",
                f"Target FPS mode: final encoding converts {current_info.fps:.6g} FPS -> exactly {fps:.6g} FPS."
            )
        filter_args = ["-vf", ",".join(video_filters)] if video_filters else []
        cmd = [
            self._tool(self.ffmpeg.get()), "-y", "-hide_banner", "-loglevel", "warning",
            "-i", str(video), "-i", str(audio_source), "-map", "0:v:0"
        ] + self._audio_map_args(audio_source, final.suffix.lower()) + filter_args + ffargs + [
            "-fps_mode:v", "cfr", "-max_interleave_delta", "0", "-shortest", "-progress", "pipe:1", "-nostats", str(final)
        ]
        rc = self._run_process(cmd, job, duration=job.info.duration, ffmpeg_progress=True, progress_callback=lambda f: self._set_stage_fraction(job, f))
        if rc != 0:
            raise BackendError(f"Final {self._selected_encode_backend()} encoding failed.")
        if not final.is_file() or final.stat().st_size <= 1024:
            raise BackendError(f"Final encoder did not create a valid output file: {final}")
        encoded_info = self._probe_video(final)
        if (encoded_info.width, encoded_info.height) != (w, h):
            raise BackendError(
                f"V247 final output geometry mismatch: expected {w}x{h} from the "
                f"verified input or explicitly selected reduction, got "
                f"{encoded_info.width}x{encoded_info.height}."
            )
        self._post("log", f"V247 final video verified: "
                         f"{encoded_info.width}x{encoded_info.height} @ "
                         f"{encoded_info.fps:.6g} FPS: {final}")
        return final

    def _video_encode_args(self, width: int, height: int, fps: float) -> List[str]:
        backend = self._selected_encode_backend()
        quality = self._selected_encode_quality()
        if backend == "NVIDIA NVENC (fast)":
            cq = NVENC_CQ_VALUES[quality]
            return [
                "-c:v", "hevc_nvenc",
                "-preset", "p7",
                "-tune", "hq",
                "-rc", "vbr",
                "-cq", str(cq),
                "-b:v", "0",
                "-multipass", "fullres",
                "-profile:v", "main10",
                "-pix_fmt", "p010le",
                "-tag:v", "hvc1",
            ]

        crf = X265_CRF_VALUES[quality]
        threads = self._selected_x265_threads()
        return [
            "-c:v", "libx265",
            "-preset", "slow",
            "-crf", str(crf),
            "-x265-params", f"pools={threads}",
            "-pix_fmt", "yuv420p10le",
            "-tag:v", "hvc1",
        ]

    def _audio_map_args(self, audio_source: Path, ext: str) -> List[str]:
        args = [
            "-map", "1:a?",
            "-af:a", "aresample=async=1000:first_pts=0",
            "-c:a", "aac", "-b:a", "192k"
        ]
        if ext == ".mkv":
            args += ["-map", "1:s?", "-c:s", "copy"]
        return args


    def _run_collect(self, cmd: List[str], job: Job, duration: float = 0.0, progress_callback: Optional[Callable[[float], None]] = None) -> Tuple[int, List[str]]:
        self._wait_if_paused()
        self._post("log", self._quote(cmd))
        flags = self._no_window()
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1, creationflags=flags)
        with self.process_lock:
            self.current_process = p
        lines: List[str] = []
        try:
            assert p.stdout is not None
            for raw in p.stdout:
                self._wait_if_paused()
                if self.stop_event.is_set():
                    self._terminate_tree(p)
                    raise Cancelled()
                line = raw.rstrip("\r\n")
                if line:
                    lines.append(line)
                    self._post("log", line)
                    if progress_callback:
                        frac = self._ffmpeg_time_from_text(line, duration)
                        if frac is not None:
                            progress_callback(frac)
            return p.wait(), lines
        finally:
            with self.process_lock:
                if self.current_process is p:
                    self.current_process = None

    def _run_process(self, cmd: List[str], job: Job, duration: float = 0.0, ffmpeg_progress: bool = False, progress_callback: Optional[Callable[[float], None]] = None, cwd: Optional[Path] = None, error_capture: Optional[List[str]] = None) -> int:
        self._wait_if_paused()
        self._post("log", self._quote(cmd))
        flags = self._no_window()
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1, creationflags=flags, cwd=str(cwd) if cwd is not None else None)
        with self.process_lock:
            self.current_process = p
        try:
            assert p.stdout is not None
            for raw in p.stdout:
                self._wait_if_paused()
                if self.stop_event.is_set():
                    self._terminate_tree(p)
                    raise Cancelled()
                line = raw.rstrip("\r\n")
                if line:
                    self._post("log", line)
                    if error_capture is not None:
                        error_capture.append(line)
                        if len(error_capture) > 120:
                            del error_capture[:60]
                    if ffmpeg_progress and progress_callback:
                        frac = self._ffmpeg_progress_fraction(line, duration)
                        if frac is not None:
                            progress_callback(frac)
            return p.wait()
        finally:
            with self.process_lock:
                if self.current_process is p:
                    self.current_process = None

    @staticmethod
    def _ffmpeg_progress_fraction(line: str, duration: float) -> Optional[float]:
        if duration <= 0:
            return None
        if line.startswith("out_time_us=") or line.startswith("out_time_ms="):
            try:
                us = int(line.split("=", 1)[1])
                return max(0.0, min(1.0, us / 1_000_000.0 / duration))
            except Exception:
                return None
        if line == "progress=end":
            return 1.0
        return None

    @staticmethod
    def _ffmpeg_time_from_text(line: str, duration: float) -> Optional[float]:
        if duration <= 0:
            return None
        m = re.search(r"time=(\d+):(\d+):(\d+(?:\.\d+)?)", line)
        if not m:
            return None
        sec = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        return max(0.0, min(1.0, sec / duration))

    @staticmethod
    def _looks_like_media_error(line: str) -> bool:
        x = line.lower()
        keys = [
            "invalid data", "corrupt", "error while decoding", "decode_slice_header error",
            "moov atom not found", "non-monotonous dts", "invalid nal", "header damaged",
            "packet corrupt", "invalid argument", "could not find codec parameters"
        ]
        return any(k in x for k in keys)


    def _highlight_stage_tab(self, stage: str):
        if not hasattr(self, "settings_nb") or not hasattr(self, "settings_tabs"):
            return
        stage_l = (stage or "").strip().lower()
        mapping = {
            "probing": ("Repair", "#B7D7F0"),
            "repairing": ("Repair", "#B7D7F0"),
            "repair": ("Repair", "#B7D7F0"),
            "fps reduce": ("FPS Reduce", "#CFE8FF"),
            "fps reduction": ("FPS Reduce", "#CFE8FF"),
            "deinterlace": ("Enhancement", "#FFD8B5"),
            "pre-ai deinterlace / enhancement": ("Enhancement", "#FFD8B5"),
            "denoise": ("Enhancement", "#FFD8B5"),
            "denoising": ("Enhancement", "#FFD8B5"),
            "extracting/decoding": ("Enhancement", "#FFD8B5"),
            "enhancement": ("Enhancement", "#FFD8B5"),
            "final image correction": ("Enhancement", "#FFD8B5"),
            "color": ("Enhancement", "#FFD8B5"),
            "color correction": ("Enhancement", "#FFD8B5"),
            "brightness": ("Enhancement", "#FFD8B5"),
            "white balance": ("Enhancement", "#FFD8B5"),
            "seedvr2 restoration 1x": ("Upscaling", "#BDE6C8"),
            "native realbasicvsr_x4 4x": ("Upscaling", "#BDE6C8"),
            "native basicvsrplusplus_x4 4x": ("Upscaling", "#BDE6C8"),
            "scaling 1 and scaling 2": ("Upscaling", "#BDE6C8"),
            "upscaling 1/3 → 2/3 → 3/3": ("Upscaling", "#BDE6C8"),
            "rife": ("RIFE", "#D8C6F0"),
            "encoding": ("Encoding", "#F7C9A9"),
        }

        for name, tab in self.settings_tabs.items():
            try:
                self.settings_nb.tab(tab, text=name)
            except tk.TclError:
                pass
        if stage_l not in mapping:
            try:
                self.ttk_style.map("Pastel.TNotebook.Tab", background=[("selected", PASTEL["blue"]), ("!selected", "#EEEAF4")])
            except Exception:
                pass
            return
        tab_name, color = mapping[stage_l]
        tab = self.settings_tabs.get(tab_name)
        if tab is not None:
            try:
                self.ttk_style.map("Pastel.TNotebook.Tab", background=[("selected", color), ("!selected", "#EEEAF4")])
                self.settings_nb.tab(tab, text=f"▶ {tab_name}")
                self.settings_nb.select(tab)
            except tk.TclError:
                pass

    def _set_stage(self, job: Job, stage: str, fraction: float, weight_start: float, weight: float):
        self.current_job_stage_name = stage
        self.current_job_stage_fraction = fraction
        self.current_job_stage_weight_start = weight_start
        self.current_job_stage_weight = weight
        job.stage = stage
        self._update_progress_from_stage(job, fraction)
        self._post("step", f"Current step: {stage}")
        self._post("stage_tab", stage)

    def _set_stage_fraction(self, job: Job, f: float):
        self.current_job_stage_fraction = max(0.0, min(1.0, f))
        self._update_progress_from_stage(job, self.current_job_stage_fraction)

    def _update_progress_from_stage(self, job: Job, f: float):
        pct = (self.current_job_stage_weight_start + self.current_job_stage_weight * max(0.0, min(1.0, f))) * 100.0
        job.progress = max(job.progress, min(99.5, pct))
        self._post("file_progress", job.progress)
        self._post("job", job)
        # V246: reflect partial progress of the active job in the queue bar.
        # The old queue bar was updated only when a whole file completed.
        ordered = self._ordered_jobs()
        if ordered:
            finished = sum(1.0 for item in ordered if item.status in ("Done", "Failed"))
            in_progress = sum(max(0.0, min(0.999, item.progress / 100.0))
                              for item in ordered if item.status == "Running")
            self._post("overall", min(99.9, 100.0 * (finished + in_progress) / len(ordered)))

    def _post(self, kind: str, value: Any):
        self.uiq.put((kind, value))

    def _drain_uiq(self):
        try:
            while True:
                kind, value = self.uiq.get_nowait()
                if kind == "log":
                    self._log(str(value))
                elif kind == "job":
                    self._update_job_row(value)
                elif kind == "queue_estimate_refresh":
                    self._update_total_queue_estimate()
                elif kind == "overall":
                    self.overall_progress.set(float(value))
                elif kind == "file_progress":
                    self.file_progress.set(float(value))
                elif kind == "eta":
                    self.eta_text.set(str(value))
                elif kind == "current_file":
                    self.current_file_text.set(str(value))
                elif kind == "step":
                    self.current_step_text.set(str(value))
                elif kind == "stage_tab":
                    self._highlight_stage_tab(str(value))
                elif kind == "temp":
                    self.temp_path_text.set(str(value))
                elif kind == "status":
                    self._log(str(value))
                elif kind == "comfy_status":
                    self.comfy_status_text.set(str(value))
                elif kind == "rife_status":
                    self.rife_status_text.set(str(value))
                elif kind == "seed_progress":
                    if 0 <= self.current_job_index < len(self.jobs) and self.current_job_stage_name == "SeedVR2":
                        self._set_stage_fraction(self.jobs[self.current_job_index], float(value))
                elif kind == "files_status":
                    self._apply_files_rows(value)
                elif kind == "files_test_status":
                    text, ok = value
                    self.files_test_status.set(str(text))
                    if ok:
                        self._log(str(text))
                    else:
                        self._log("INSTALLATION TEST FAILED: " + str(text))
                elif kind == "root_scan_result":
                    self._apply_root_scan_result(value)
                elif kind == "vram_spill":
                    self._apply_vram_spill(value)
                elif kind == "queue_finished_ui":
                    clean_finish = bool(value)
                    if clean_finish:
                        self.overall_progress.set(100.0)
                        self.file_progress.set(100.0)
                        self.eta_text.set("ETA: 00:00")
                        self.current_file_text.set("Current file: queue finished")
                        self.current_step_text.set("Current step: complete")
                        self.rife_status_text.set("RIFE: --")
                        self._highlight_stage_tab("complete")
                    else:
                        self.eta_text.set("ETA: --")
                elif kind == "refresh_preview":
                    self._refresh_preview()
                elif kind == "save_exit_success":
                    self._log("Obsolete saved-checkpoint completion event ignored.")
                elif kind == "save_exit_failure":
                    self._save_exit_checkpoint_in_progress = False
                    if self.pause_event.is_set():
                        self.resume_btn.configure(state="normal")
                        self.pause_btn.configure(text="PAUSED", style="Pause.TButton")
                        self._set_processing_highlight("paused")
                        self.save_exit_btn.configure(state="disabled")
                        self.current_step_text.set("Current step: PAUSED - computation state preserved")
                        self.eta_text.set("ETA: PAUSED")
                    self.stop_btn.configure(state="normal" if self.worker and self.worker.is_alive() else "disabled")
                    messagebox.showerror(
                        APP_NAME,
                        f"Could not save the processing state: {value}",
                    )
                elif kind == "worker_done":
                    self.pause_event.clear()
                    self._paused_process_pids = []
                    self._pause_started_at = None
                    self.current_process = None
                    self.start_btn.configure(state="normal", text="START QUEUE", style="Start.TButton")
                    self._set_processing_highlight("idle")
                    self.stop_btn.configure(state="disabled")
                    self.pause_btn.configure(state="disabled", text="PAUSE", style="Pause.TButton")
                    self.resume_btn.configure(state="disabled")
                    self.save_exit_btn.configure(state="disabled", style="SaveExit.TButton")

        except queue.Empty:
            pass
        self.after(120, self._drain_uiq)

    def _tick_eta(self):


        if 0 <= self.current_job_index < len(self.jobs):
            _elapsed_job = self.jobs[self.current_job_index]
            self._refresh_job_elapsed_display(
                _elapsed_job,
                force=False,
                update_row=True,
            )

        if self.pause_event.is_set():
            self.eta_text.set("ETA: PAUSED")
            self.after(1000, self._tick_eta)
            return

        if 0 <= self.current_job_index < len(self.jobs):
            j = self.jobs[self.current_job_index]
            if j.status == "Done" or j.progress >= 100:
                j.eta = "00:00"
                self.eta_text.set("ETA: 00:00")
                self.file_progress.set(100.0)
                self._update_job_row(j)
            elif j.started_at > 0:
                elapsed = max(0.0, self._job_elapsed_now(j))
                if (self.current_job_stage_name.lower().startswith("native ")
                        and j.native_vsr_frames_done > 0
                        and j.native_vsr_stage_eta_seconds is not None):
                    # Measured completed-frame throughput, not a guessed total ETA.
                    remain = max(0.0, float(j.native_vsr_stage_eta_seconds)
                                 - max(0.0, self._job_elapsed_now(j)
                                           - j.native_vsr_eta_reference_elapsed))
                    j.eta = self._fmt_time(remain)
                    self.eta_text.set(f"Native 4X stage remaining: {j.eta} (then SeedVR2 etc.)")
                    self._update_job_row(j)
                elif j.estimated_seconds is not None and float(j.estimated_seconds) > 0:
                    remain = max(0.0, float(j.estimated_seconds) - elapsed)
                    j.eta = self._fmt_time(remain)
                    self.eta_text.set(f"ETA: {j.eta}")
                    self._update_job_row(j)
                    self.eta_text.set(f"ETA: {j.eta}")
                    self._update_job_row(j)
                elif j.progress > 0.5:
                    total_est = elapsed / max(0.005, (j.progress / 100.0))
                    remain = max(0.0, total_est - elapsed)
                    j.eta = self._fmt_time(remain)
                    self.eta_text.set(f"ETA: {j.eta}")
                    self._update_job_row(j)

        self.after(1000, self._tick_eta)

    @staticmethod
    def _filetime_to_int(ft):
        return (int(ft.dwHighDateTime) << 32) | int(ft.dwLowDateTime)

    def _read_cpu_percent(self):
        try:
            idle = wintypes.FILETIME()
            kernel = wintypes.FILETIME()
            user = wintypes.FILETIME()
            ok = ctypes.windll.kernel32.GetSystemTimes(
                ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)
            )
            if not ok:
                return None
            current = (
                self._filetime_to_int(idle),
                self._filetime_to_int(kernel),
                self._filetime_to_int(user),
            )
            previous = self._cpu_prev_times
            self._cpu_prev_times = current
            if previous is None:
                return None
            idle_delta = current[0] - previous[0]
            kernel_delta = current[1] - previous[1]
            user_delta = current[2] - previous[2]
            total = kernel_delta + user_delta
            if total <= 0:
                return None
            busy = max(0, total - idle_delta)
            return max(0.0, min(100.0, (busy * 100.0) / total))
        except Exception:
            return None

    def _find_nvidia_smi(self):
        if self._nvidia_smi_path and Path(self._nvidia_smi_path).is_file():
            return self._nvidia_smi_path
        candidates = []
        found = shutil.which("nvidia-smi") or shutil.which("nvidia-smi.exe")
        if found:
            candidates.append(found)
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        windir = os.environ.get("WINDIR", r"C:\Windows")
        candidates.extend([
            str(Path(pf) / "NVIDIA Corporation" / "NVSMI" / "nvidia-smi.exe"),
            str(Path(windir) / "System32" / "nvidia-smi.exe"),
        ])
        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                self._nvidia_smi_path = str(candidate)
                return self._nvidia_smi_path
        return None

    def _read_nvidia_gpu_name(self) -> str:
        if self._gpu_name_cache:
            return str(self._gpu_name_cache)

        exe = self._find_nvidia_smi()
        if not exe:
            return "GPU 0"

        cmd = [
            exe,
            "--query-gpu=name",
            "--format=csv,noheader",
            "--id=0",
        ]
        kwargs = dict(
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2.5,
        )
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        try:
            cp = subprocess.run(cmd, **kwargs)
            if cp.returncode == 0:
                name = next(
                    (ln.strip() for ln in cp.stdout.splitlines() if ln.strip()),
                    "",
                )
                if name:
                    self._gpu_name_cache = name
                    return name
        except Exception:
            pass

        return "GPU 0"

    def _read_nvidia_stats(self):
        exe = self._find_nvidia_smi()
        if not exe:
            return None
        cmd = [
            exe,
            "--query-gpu=utilization.gpu,memory.used,memory.total",
            "--format=csv,noheader,nounits",
            "--id=0",
        ]
        kwargs = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2.5)
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            cp = subprocess.run(cmd, **kwargs)
            if cp.returncode != 0:
                return None
            line = next((ln.strip() for ln in cp.stdout.splitlines() if ln.strip()), "")
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 3:
                return None
            gpu = float(parts[0])
            used = float(parts[1])
            total = float(parts[2])
            return max(0.0, min(100.0, gpu)), max(0.0, used), max(0.0, total)
        except Exception:
            return None

    def _read_windows_shared_gpu_mib(self) -> Optional[float]:
        if os.name != "nt":
            return None
        ps = shutil.which("powershell.exe") or os.path.join(
            os.environ.get("SystemRoot", r"C:\Windows"), "System32", "WindowsPowerShell", "v1.0", "powershell.exe"
        )
        if not os.path.isfile(ps):
            return None
        script = (
            "$ErrorActionPreference='Stop'; "
            r"$c=(Get-Counter '\GPU Adapter Memory(*)\Shared Usage').CounterSamples; "
            "$s=($c | Measure-Object -Property CookedValue -Sum).Sum; "
            "if($null -eq $s){$s=0}; "
            "[Console]::Write([string]([math]::Round($s/1MB,2)))"
        )
        kwargs = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=4.0)
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            cp = subprocess.run([ps, "-NoProfile", "-NonInteractive", "-Command", script], **kwargs)
            if cp.returncode != 0:
                return None
            return max(0.0, float(cp.stdout.strip().replace(",", ".")))
        except Exception:
            return None

    def _poll_vram_spill_worker(self):
        try:
            value = self._read_windows_shared_gpu_mib()
            self._post("vram_spill", value)
        finally:
            self._spill_poll_busy = False

    def _apply_vram_spill(self, shared_mib):
        self._spill_mib = shared_mib
        if shared_mib is None:
            self._spill_delta_mib = 0.0
            self.vram_spill_usage.set(0.0)
            self.vram_spill_text.set("Shared GPU: N/A")
            if hasattr(self, "vram_spill_label"):
                self.vram_spill_label.configure(style="Spill.Normal.TLabel")
            if hasattr(self, "vram_spill_bar"):
                self.vram_spill_bar.configure(style="Horizontal.TProgressbar")
            return

        shared_mib = max(0.0, float(shared_mib))
        shared_gb = shared_mib / 1024.0
        dedicated_pct = float(self.vram_usage.get())
        stage_l = self.current_job_stage_name.lower()
        seed_active = self.comfy_job_active and stage_l == "seedvr2"
        native_active = stage_l.startswith("native ") and "vsr" in stage_l
        ai_active = seed_active or native_active

        if not ai_active:
            self._shared_baseline_mib = shared_mib
            self._spill_delta_mib = 0.0
            self._spill_consecutive = 0
            self._spill_warning_active = False
            self.vram_spill_usage.set(min(100.0, shared_mib * 100.0 / max(self._vram_total_mib, 12288.0)))
            self.vram_spill_text.set(f"Shared GPU: {shared_gb:.2f} GB")
            if hasattr(self, "vram_spill_label"):
                self.vram_spill_label.configure(style="Spill.Normal.TLabel")
            if hasattr(self, "vram_spill_bar"):
                self.vram_spill_bar.configure(style="Horizontal.TProgressbar")
            return

        baseline = self._shared_baseline_mib
        if baseline is None:
            baseline = shared_mib
            self._shared_baseline_mib = baseline
        delta_mib = max(0.0, shared_mib - float(baseline))
        self._spill_delta_mib = delta_mib
        delta_gb = delta_mib / 1024.0
        total = self._vram_total_mib if self._vram_total_mib > 0 else 12288.0
        self.vram_spill_usage.set(max(0.0, min(100.0, shared_mib * 100.0 / total)))


        critical_pressure = dedicated_pct >= 99.0 and delta_mib >= 768.0
        if critical_pressure:
            self._spill_consecutive += 1
        else:
            self._spill_consecutive = 0

        if self._spill_consecutive >= 3:
            self.vram_spill_text.set(f"VRAM PRESSURE: +{delta_gb:.2f} GB")
            if hasattr(self, "vram_spill_label"):
                self.vram_spill_label.configure(style="Spill.Red.TLabel")
            if hasattr(self, "vram_spill_bar"):
                self.vram_spill_bar.configure(style="Spill.Horizontal.TProgressbar")
            if not self._spill_warning_active:
                self._spill_warning_active = True
                if native_active:
                    self._log(
                        f"V246 WARNING: neural VSR memory pressure: dedicated={dedicated_pct:.0f}%, "
                        f"shared GPU={shared_gb:.2f} GB (+{delta_gb:.2f} GB above baseline). "
                        "Very slow 4X neural inference is likely if shared system GPU memory "
                        "is being used heavily. Consider a smaller explicit pre-neural reduction "
                        "(e.g. 0.50X) for a future run; this run's user settings are not altered."
                    )
                else:
                    self._log(
                        f"WARNING: critical VRAM pressure display: dedicated={dedicated_pct:.0f}%, "
                        f"Shared GPU={shared_gb:.2f} GB (+{delta_gb:.2f} GB above baseline). "
                        "This is telemetry only; V62 will reduce SeedVR2 batch size only if CUDA/ComfyUI reports an actual allocation/OOM failure."
                    )
        else:
            self._spill_warning_active = False
            self.vram_spill_text.set(f"Shared GPU: {shared_gb:.2f} GB")
            if hasattr(self, "vram_spill_label"):
                self.vram_spill_label.configure(style="Spill.Normal.TLabel")
            if hasattr(self, "vram_spill_bar"):
                self.vram_spill_bar.configure(style="Horizontal.TProgressbar")

    def _tick_resources(self):
        cpu = self._read_cpu_percent()
        if cpu is not None:
            self.cpu_usage.set(cpu)
            self.cpu_usage_text.set(f"CPU: {cpu:.0f}%")
        else:
            self.cpu_usage_text.set("CPU: --%")

        stats = self._read_nvidia_stats()
        if stats is not None:
            gpu, used_mib, total_mib = stats
            self.gpu_usage.set(gpu)
            self.gpu_usage_text.set(f"GPU: {gpu:.0f}%")
            used_gb = 0.0
            total_gb = 0.0
            if total_mib > 0:
                self._vram_total_mib = total_mib
                pct = max(0.0, min(100.0, used_mib * 100.0 / total_mib))
                self.vram_usage.set(pct)
                used_gb = used_mib / 1024.0
                total_gb = total_mib / 1024.0
                self.vram_usage_text.set(f"VRAM: {used_gb:.1f} / {total_gb:.1f} GB")
                if hasattr(self, "vram_bar"):
                    self.vram_bar.configure(style="Critical.Horizontal.TProgressbar" if pct >= 90.0 else "Horizontal.TProgressbar")
            else:
                self.vram_usage.set(0.0)
                self.vram_usage_text.set("VRAM: --")

            if self._rife_runtime_active:
                gpu_name = self._rife_runtime_gpu_name or self._read_nvidia_gpu_name()
                throughput = float(self._rife_runtime_output_fps or 0.0)
                throughput_text = f"{throughput:.2f} output fps" if throughput > 0 else "waiting for frames"
                vram_text = (
                    f"{used_gb:.1f}/{total_gb:.1f} GB"
                    if total_gb > 0
                    else "--"
                )
                self.rife_status_text.set(
                    f"RIFE GPU: {gpu_name} | ncnn-Vulkan | device 0 | "
                    f"threads {self._rife_runtime_gpu_thread or '?'} | "
                    f"GPU {gpu:.0f}% | VRAM {vram_text} | {throughput_text}"
                )
        else:
            self.gpu_usage.set(0.0)
            self.vram_usage.set(0.0)
            self.gpu_usage_text.set("GPU: N/A")
            self.vram_usage_text.set("VRAM: N/A")
            if self._rife_runtime_active:
                self.rife_status_text.set(
                    f"RIFE GPU: {self._rife_runtime_gpu_name or 'GPU 0'} | "
                    f"ncnn-Vulkan | device 0 | threads {self._rife_runtime_gpu_thread or '?'} | GPU telemetry unavailable"
                )


        if os.name == "nt" and not self._spill_poll_busy:
            self._spill_poll_busy = True
            threading.Thread(target=self._poll_vram_spill_worker, daemon=True).start()

        self.after(1000, self._tick_resources)

    def _log(self, text: str):
        line = text.rstrip() + "\n"
        self.log.configure(state="normal")
        self.log.insert("end", line)
        self.log.see("end")
        self.log.configure(state="disabled")
        if self.active_log_path is not None:
            try:
                self.active_log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.active_log_path.open("a", encoding="utf-8", errors="replace") as fh:
                    fh.write(line)
            except Exception:
                pass

    def _clear_live_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")


    @staticmethod
    def _resolved_tool(value: str) -> Optional[Path]:
        value = (value or "").strip()
        if not value:
            return None
        p = Path(value)
        if p.is_file():
            return p
        found = shutil.which(value)
        return Path(found) if found else None

    def _find_seed_files(self) -> Dict[str, Optional[Path]]:
        root = Path(self.comfy_root.get().strip())
        comfy = root / "ComfyUI"
        result: Dict[str, Optional[Path]] = {"node": None, "model": None, "vae": None}
        custom = comfy / "custom_nodes"
        exact = custom / "ComfyUI-SeedVR2-LongVideo"
        if exact.is_dir():
            result["node"] = exact
        elif custom.is_dir():
            try:
                cands = [x for x in custom.iterdir() if x.is_dir() and "seedvr2" in x.name.lower()]
                if cands:
                    result["node"] = sorted(cands, key=lambda x: x.name.lower())[0]
            except Exception:
                pass

        models = comfy / "models"
        if models.is_dir():
            exact_model = list(models.rglob("seedvr2_3b_int8_convrot.safetensors"))
            exact_vae = list(models.rglob("seedvr2_ema_vae_fp16.safetensors"))
            if exact_model:
                result["model"] = exact_model[0]
            else:
                try:
                    cands = [x for x in models.rglob("*.safetensors") if "seedvr2" in x.name.lower() and "3b" in x.name.lower()]
                    if cands:
                        result["model"] = cands[0]
                except Exception:
                    pass
            if exact_vae:
                result["vae"] = exact_vae[0]
            else:
                try:
                    cands = [x for x in models.rglob("*.safetensors") if "seedvr2" in x.name.lower() and "vae" in x.name.lower()]
                    if cands:
                        result["vae"] = cands[0]
                except Exception:
                    pass
        return result

    def _vapoursynth_probe(self, execute_rife: bool = False) -> Tuple[bool, str]:
        vsp = self._resolved_tool(self.vspipe.get())
        if not vsp:
            return False, "vspipe.exe/vspipe.bat not found"
        dll = self.rife_plugin_dll.get().strip()
        if not dll or not Path(dll).is_file():
            return False, "Native RIFE DLL not found. Expected e.g. librife_windows_x86-64.dll"
        model_path = self.rife_model_path.get().strip()
        with tempfile.TemporaryDirectory(prefix="UpscalerV62_RIFE_") as td:
            vpy = Path(td) / "verify_rife.vpy"
            dll_lit = repr(dll)
            model_lit = repr(model_path)
            if execute_rife:
                if not (model_path and (Path(model_path) / "flownet.param").is_file() and (Path(model_path) / "flownet.bin").is_file()):
                    return False, "RIFE model folder is missing or incomplete. Expected flownet.param and flownet.bin."
                call = f'core.rife.RIFE(clip, model_path={model_lit}, factor_num=2, factor_den=1, gpu_id=0, gpu_thread=1)'
                script = f'''import vapoursynth as vs
core = vs.core
if not hasattr(core, "rife"):
    core.std.LoadPlugin(path={dll_lit})
if not hasattr(core, "rife"):
    raise RuntimeError("RIFE DLL loaded but core.rife was not registered")
clip = core.std.BlankClip(width=64, height=64, length=2, fpsnum=24, fpsden=1, format=vs.RGBS)
clip = {call}
clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_s="709")
clip.set_output()
'''
                args = [str(vsp), "-c", "y4m", str(vpy), "-"]
                stdout_target = subprocess.DEVNULL
            else:
                script = f'''import vapoursynth as vs
core = vs.core
if not hasattr(core, "rife"):
    core.std.LoadPlugin(path={dll_lit})
if not hasattr(core, "rife"):
    raise RuntimeError("RIFE DLL loaded but core.rife was not registered")
clip = core.std.BlankClip(width=64, height=64, length=1, fpsnum=24, fpsden=1, format=vs.YUV420P8)
clip.set_output()
'''
                args = [str(vsp), "--info", str(vpy), "-"]
                stdout_target = subprocess.PIPE
            vpy.write_text(script, encoding="utf-8")
            cp = subprocess.run(
                args, stdout=stdout_target, stderr=subprocess.PIPE, text=False,
                timeout=90 if execute_rife else 30, creationflags=self._no_window(),
                env=self._vapoursynth_env()
            )
            err = (cp.stderr or b"").decode("utf-8", errors="replace").strip()
            if cp.returncode != 0:
                return False, err[-900:] or f"vspipe exited with code {cp.returncode}"
            if execute_rife:
                return True, f"RIFE GPU test passed | DLL: {dll} | model folder: {model_path}"
            return True, f"RIFE plugin available (autoloaded or loaded explicitly) | {dll}"

    def _vapoursynth_source_probe(self) -> Tuple[bool, str]:
        vsp = self._resolved_tool(self.vspipe.get())
        if not vsp:
            return False, "vspipe.exe/vspipe.bat not found"
        source_dll = self.vs_source_plugin_dll.get().strip()
        with tempfile.TemporaryDirectory(prefix="UpscalerV62_VSSOURCE_") as td:
            vpy = Path(td) / "verify_source.vpy"
            source_lit = repr(source_dll)
            script = f'''import vapoursynth as vs
core = vs.core
_source_dll = {source_lit}
if _source_dll and not (hasattr(core, "bs") or hasattr(core, "lsmas") or hasattr(core, "ffms2")):
    core.std.LoadPlugin(path=_source_dll)
if hasattr(core, "bs"):
    source = "BestSource (core.bs)"
elif hasattr(core, "lsmas"):
    source = "L-SMASH-Works (core.lsmas)"
elif hasattr(core, "ffms2"):
    source = "FFMS2 (core.ffms2)"
else:
    raise RuntimeError("No VapourSynth video source plugin found. Recommended contained install: <ComfyUI embedded python> -m pip install --no-deps vapoursynth-bestsource")
clip = core.std.BlankClip(width=64, height=64, length=1, fpsnum=24, fpsden=1, format=vs.YUV420P8)
clip.set_output()
'''
            vpy.write_text(script, encoding="utf-8")
            cp = subprocess.run(
                [str(vsp), "--info", str(vpy), "-"], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=False, timeout=30,
                creationflags=self._no_window(), env=self._vapoursynth_env()
            )
            err = (cp.stderr or b"").decode("utf-8", errors="replace").strip()
            if cp.returncode != 0:
                return False, err[-900:] or f"vspipe exited with code {cp.returncode}"
            detail = "BestSource/L-SMASH-Works/FFMS2 available"
            if source_dll:
                detail += f" | explicit DLL: {source_dll}"
            return True, detail

    def _collect_files_status(self, deep: bool = False) -> List[Tuple[str, str, str, str]]:
        rows: List[Tuple[str, str, str, str]] = []

        def add(name: str, ok: bool, detail: str, warn: bool = False):
            status = "OK" if ok else ("CHECK" if warn else "MISSING")
            tag = "ok" if ok else ("warn" if warn else "bad")
            rows.append((name, status, detail, tag))

        ffmpeg = self._resolved_tool(self.ffmpeg.get())
        ffprobe = self._resolved_tool(self.ffprobe.get())
        vspipe = self._resolved_tool(self.vspipe.get())
        add("FFmpeg", bool(ffmpeg), str(ffmpeg) if ffmpeg else self.ffmpeg.get())
        add("FFprobe", bool(ffprobe), str(ffprobe) if ffprobe else self.ffprobe.get())


        seed_needed = self._selected_engine() == "SeedVR2"
        root = Path(self.comfy_root.get().strip())
        comfy = root / "ComfyUI"
        add("ComfyUI root", comfy.is_dir(), str(comfy), warn=not seed_needed)
        py = root / "python_embeded" / "python.exe"
        main = comfy / "main.py"
        add("ComfyUI embedded Python", py.is_file(), str(py), warn=not seed_needed)
        add("ComfyUI main.py", main.is_file(), str(main), warn=not seed_needed)

        seed = self._find_seed_files()
        add("SeedVR2 custom node", bool(seed["node"]), str(seed["node"] or "Not found under ComfyUI\\custom_nodes"), warn=not seed_needed)
        add("SeedVR2 3B INT8 model", bool(seed["model"]), str(seed["model"] or "seedvr2 3B model not found under ComfyUI\\models"), warn=not seed_needed)
        add("SeedVR2 VAE", bool(seed["vae"]), str(seed["vae"] or "SeedVR2 VAE not found under ComfyUI\\models"), warn=not seed_needed)

        wf_path = Path(self.workflow_json.get().strip())
        wf_ok = False
        wf_detail = str(wf_path) if self.workflow_json.get().strip() else "No API workflow selected"
        if wf_path.is_file():
            try:
                wf = self._load_api_workflow()
                seed_nodes = [n for n in wf.values() if "seedvr2" in str(n.get("class_type", "")).lower()]
                wf_ok = bool(seed_nodes)
                wf_detail = f"{wf_path} | {len(seed_nodes)} SeedVR2 node(s)"
            except Exception as e:
                wf_detail = f"{wf_path} | {e}"
        add("SeedVR2 API workflow", wf_ok, wf_detail, warn=not seed_needed)

        vsr_mode = str(self.preseed_mode.get() or "Only Bicubic")
        needs_vsr = vsr_mode != "Only Bicubic" and seed_needed
        vsr_python_str = str(self.native_sr_python.get() or "").strip().strip('"')
        vsr_python = Path(vsr_python_str) if vsr_python_str else None
        vsr_repo_str = str(self.native_sr_repo.get() or "").strip().strip('"')
        vsr_repo = Path(vsr_repo_str) if vsr_repo_str else None
        vsr_config = Path(str(self.native_sr_config.get() or "").strip().strip('"'))
        vsr_checkpoint = Path(str(self.native_sr_checkpoint.get() or "").strip().strip('"'))
        script_name = "demo/restoration_video_demo.py" if vsr_mode.startswith("BasicVSR++") else "inference_realbasicvsr.py"
        vsr_script = (vsr_repo / script_name) if vsr_repo else None
        add("VSR Python", bool(vsr_python and vsr_python.is_file()), vsr_python_str or "Not configured", warn=not needs_vsr)
        add("VSR repository", bool(vsr_repo and vsr_repo.is_dir()), vsr_repo_str or "Not configured", warn=not needs_vsr)
        add("VSR inference script", bool(vsr_script and vsr_script.is_file()), str(vsr_script or "Not configured"), warn=not needs_vsr)
        add("VSR config", vsr_config.is_file(), str(vsr_config), warn=not needs_vsr)
        add("VSR checkpoint", vsr_checkpoint.is_file(), str(vsr_checkpoint), warn=not needs_vsr)

        add("VapourSynth vspipe", bool(vspipe), str(vspipe) if vspipe else self.vspipe.get())
        model_path = self.rife_model_path.get().strip()
        model_ok = bool(model_path and (Path(model_path) / "flownet.param").is_file() and (Path(model_path) / "flownet.bin").is_file())
        add("RIFE model", model_ok, model_path if model_path else "No RIFE model folder found (needs flownet.param + flownet.bin)")

        if vspipe:
            try:
                ok, detail = self._vapoursynth_probe(execute_rife=deep)
                add("VapourSynth RIFE plugin", ok, detail)
            except Exception as e:
                add("VapourSynth RIFE plugin", False, str(e))
            try:
                src_ok, src_detail = self._vapoursynth_source_probe()
                add("VapourSynth video source plugin", src_ok, src_detail)
            except Exception as e:
                add("VapourSynth video source plugin", False, str(e))
        else:
            add("VapourSynth RIFE plugin", False, "Cannot test without vspipe.exe/vspipe.bat")
            add("VapourSynth video source plugin", False, "Cannot test without vspipe.exe/vspipe.bat")

        if deep and ffmpeg:


            try:
                enc_list = subprocess.run(
                    [str(ffmpeg), "-hide_banner", "-encoders"], stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, timeout=30, creationflags=self._no_window()
                ).stdout.decode("utf-8", errors="replace")
            except Exception:
                enc_list = ""
            final_encoder_tests = (
                ("H.265 NVENC", "hevc_nvenc", ["-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", "24", "-b:v", "0", "-pix_fmt", "p010le"]),
                ("libx265", "libx265", ["-preset", "medium", "-crf", "24", "-pix_fmt", "yuv420p10le"]),
            )
            for label, enc, enc_args in final_encoder_tests:
                if enc not in enc_list:
                    add(label, False, f"{enc} is not present in this FFmpeg build")
                    continue
                try:
                    with tempfile.TemporaryDirectory(prefix="UpscalerV101_HEVC_") as td:
                        out = Path(td) / "test_hevc.mp4"
                        cmd = [
                            str(ffmpeg), "-y", "-hide_banner", "-loglevel", "error",
                            "-f", "lavfi", "-i", "testsrc2=size=320x240:rate=30:duration=1",
                            "-an", "-c:v", enc,
                        ] + enc_args + [
                            "-frames:v", "30", "-tag:v", "hvc1", str(out)
                        ]
                        cp = subprocess.run(
                            cmd,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE,
                            timeout=90,
                            creationflags=self._no_window(),
                        )
                        err = (cp.stderr or b"").decode("utf-8", errors="replace").strip()
                        passed = cp.returncode == 0 and out.is_file() and out.stat().st_size > 0
                        add(label, passed, "30-frame HEVC encode test passed" if passed else (err[-900:] or f"FFmpeg exit code {cp.returncode}"))
                except Exception as e:
                    add(label, False, str(e))
        return rows

    @staticmethod
    def _compact_file_detail(detail: str, max_chars: int = 180) -> str:
        text = " ".join(str(detail).replace("\r", "\n").split())
        if len(text) > max_chars:
            return text[:max_chars - 1] + "…"
        return text

    def _apply_files_rows(self, rows):
        if not hasattr(self, "files_tree"):
            return
        self._files_full_details = {}
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        for name, status, detail, tag in rows:
            item = self.files_tree.insert("", "end", values=(name, status, str(detail)), tags=(tag,))
            self._files_full_details[item] = str(detail)
        self._show_selected_file_detail()

    def _sort_files_column(self, col: str):
        if not hasattr(self, "files_tree"):
            return
        reverse = self._files_sort_reverse.get(col, False)
        items = list(self.files_tree.get_children(""))
        items.sort(key=lambda item: str(self.files_tree.set(item, col)).strip().casefold(), reverse=reverse)
        for index, item in enumerate(items):
            self.files_tree.move(item, "", index)
        self._files_sort_reverse[col] = not reverse
        labels = {"component": "Component", "status": "Status", "location": "Location / details"}
        for c, label in labels.items():
            suffix = " ▲" if c == col and reverse else (" ▼" if c == col else "")
            self.files_tree.heading(c, text=label + suffix, command=lambda cc=c: self._sort_files_column(cc))

    def _show_selected_file_detail(self, _event=None):
        if not hasattr(self, "files_detail_text"):
            return
        sel = self.files_tree.selection() if hasattr(self, "files_tree") else ()
        if sel:
            item = sel[0]
            vals = self.files_tree.item(item, "values")
            detail = self._files_full_details.get(item, str(vals[2]) if len(vals) > 2 else "")
            title = f"{vals[0]} — {vals[1]}\n" if vals else ""
            text = title + detail
        else:
            text = "Select a row to see the complete path or error message."
        self.files_detail_text.configure(state="normal")
        self.files_detail_text.delete("1.0", "end")
        self.files_detail_text.insert("1.0", text)
        self.files_detail_text.configure(state="disabled")

    def _fix_selected_file_item(self):
        if not hasattr(self, "files_tree"):
            return
        sel = self.files_tree.selection()
        if not sel:
            messagebox.showinfo(APP_NAME, "Select a row in the Files tab first, then click 'Browse / Fix selected...'.")
            return
        values = self.files_tree.item(sel[0], "values")
        if not values:
            return
        component = str(values[0])

        if component in {"VSR Python", "VSR config", "VSR checkpoint"}:
            var = {"VSR Python": self.native_sr_python,
                   "VSR config": self.native_sr_config,
                   "VSR checkpoint": self.native_sr_checkpoint}[component]
            ext = {"VSR Python": "*.exe", "VSR config": "*.py", "VSR checkpoint": "*.pth"}[component]
            p = filedialog.askopenfilename(title=f"Locate {component}",
                                           filetypes=[(component, ext), ("All files", "*")])
            if p:
                var.set(p)
        elif component in {"VSR repository", "VSR inference script"}:
            p = filedialog.askdirectory(title="Select VSR repository folder")
            if p:
                self.native_sr_repo.set(p)

        elif component == "SeedVR2 API workflow":
            p = filedialog.askopenfilename(
                title="Select SeedVR2 API workflow JSON",
                filetypes=[("ComfyUI API workflow", "*.json"), ("All files", "*")]
            )
            if p:
                self.workflow_json.set(p)
                try:
                    self._load_api_workflow()
                    messagebox.showinfo(APP_NAME, "SeedVR2 API workflow selected and validated.")
                except Exception as e:
                    messagebox.showerror(APP_NAME, f"The selected JSON is not a usable ComfyUI API workflow:\n\n{e}")

        elif component == "VapourSynth vspipe":
            p = filedialog.askopenfilename(
                title="Locate vspipe.exe",
                filetypes=[("vspipe.exe", "vspipe.exe"), ("Executable", "*.exe"), ("All files", "*")]
            )
            if p:
                self.vspipe.set(p)

        elif component == "FFmpeg":
            p = filedialog.askopenfilename(title="Locate ffmpeg.exe", filetypes=[("ffmpeg.exe", "ffmpeg.exe"), ("Executable", "*.exe"), ("All files", "*")])
            if p:
                self.ffmpeg.set(p)

        elif component == "FFprobe":
            p = filedialog.askopenfilename(title="Locate ffprobe.exe", filetypes=[("ffprobe.exe", "ffprobe.exe"), ("Executable", "*.exe"), ("All files", "*")])
            if p:
                self.ffprobe.set(p)

        elif component in {"ComfyUI root", "ComfyUI embedded Python", "ComfyUI main.py"}:
            p = filedialog.askdirectory(title="Select ComfyUI portable root (folder containing ComfyUI and python_embeded)")
            if p:
                self.comfy_root.set(p)

        elif component in {"SeedVR2 custom node", "SeedVR2 3B INT8 model", "SeedVR2 VAE"}:
            messagebox.showinfo(
                APP_NAME,
                "These SeedVR2 files are discovered automatically inside the selected ComfyUI portable root.\n\n"
                "Use Tools / ComfyUI → ComfyUI portable root → Browse... and select the folder that contains both 'ComfyUI' and 'python_embeded'."
            )

        elif component == "VapourSynth RIFE plugin":
            p = filedialog.askopenfilename(
                title="Select the native VapourSynth RIFE plugin DLL",
                filetypes=[("RIFE plugin DLL", "*.dll"), ("All files", "*")]
            )
            if p:
                dll = Path(p)
                self.rife_plugin_dll.set(str(dll))
                self.rife_plugin_dir.set(str(dll.parent))
                messagebox.showinfo(
                    APP_NAME,
                    f"RIFE DLL selected:\n{dll}\n\nV62 can use a RIFE model folder elsewhere under the Upscaling root; SCAN ROOT will locate flownet.param + flownet.bin automatically."
                )
        elif component == "RIFE model":
            p = filedialog.askdirectory(title="Select RIFE model folder containing flownet.param and flownet.bin")
            if p:
                model = Path(p)
                if not (model / "flownet.param").is_file() or not (model / "flownet.bin").is_file():
                    messagebox.showerror(APP_NAME, "That folder does not contain both flownet.param and flownet.bin.")
                else:
                    self.rife_model_path.set(str(model))
        elif component == "VapourSynth video source plugin":
            p = filedialog.askopenfilename(
                title="Select BestSource / L-SMASH-Works / FFMS2 VapourSynth DLL",
                filetypes=[("VapourSynth plugin DLL", "*.dll"), ("All files", "*")]
            )
            if p:
                self.vs_source_plugin_dll.set(p)
        else:
            messagebox.showinfo(APP_NAME, f"No manual browse action is required for: {component}")

        self.after(200, self._refresh_files_status)

    def _schedule_files_status_refresh(self):
        pending = getattr(self, "_files_refresh_after_id", None)
        if pending:
            try:
                self.after_cancel(pending)
            except Exception:
                pass
        self._files_refresh_after_id = self.after(450, self._refresh_files_status)

    def _refresh_files_status(self):
        if hasattr(self, "files_test_status"):
            self.files_test_status.set("Verifying required files...")
        threading.Thread(target=self._refresh_files_status_worker, daemon=True).start()

    def _refresh_files_status_worker(self):
        try:
            rows = self._collect_files_status(deep=False)
            self._post("files_status", rows)
            missing = [r for r in rows if r[1] == "MISSING"]
            if hasattr(self, "files_test_status"):
                text = "File verification: all required components found" if not missing else f"File verification: {len(missing)} item(s) missing"
                self._post("files_test_status", (text, not missing))
        except Exception as e:
            self._post("files_test_status", (f"Verification error: {e}", False))

    def _test_installation_button(self):
        if self.worker and self.worker.is_alive():
            messagebox.showwarning(APP_NAME, "Wait until the current video queue is finished before running the installation test.")
            return
        self.files_test_status.set("Installation test: running...")
        threading.Thread(target=self._test_installation_worker, daemon=True).start()

    def _test_installation_worker(self):
        try:
            rows = self._collect_files_status(deep=True)
            failures = [r for r in rows if r[1] == "MISSING"]
            self._post("files_status", rows)
            if failures:
                names = ", ".join(r[0] for r in failures)
                self._post("files_test_status", (f"Installation test failed: {names}", False))
                return

            if True:
                self._post("log", "Installation test: starting hidden ComfyUI and checking its API...")
                self._load_api_workflow()
                self._ensure_hidden_comfy()
                if not self._comfy_ping():
                    raise BackendError("Hidden ComfyUI did not answer the API health check.")

            self._post("log", "Installation test: executing a tiny in-memory RIFE GPU test...")
            ok, detail = self._vapoursynth_probe(execute_rife=True)
            if not ok:
                raise BackendError("RIFE runtime test failed: " + detail)

            self._post("files_test_status", ("Installation test: PASS - selected AI backend, RIFE, HEVC NVENC and libx265 are available", True))
        except Exception as e:
            self._post("files_test_status", (f"Installation test: FAIL - {e}", False))


    def _basic_validate(self) -> bool:
        try:
            self._require_tool(self.ffmpeg.get(), "FFmpeg")
            self._require_tool(self.ffprobe.get(), "FFprobe")

            if self._job_setting("fps_reduce_mode", self.fps_reduce_mode) not in FPS_REDUCE_MODES:
                raise BackendError("FPS Reduce mode is invalid.")
            if float(self._job_setting("fps_reduce_max", self.fps_reduce_max)) < 1.0:
                raise BackendError("Maximum FPS must be at least 1 FPS.")
            if self._job_setting("rife_mode", self.rife_mode) not in RIFE_MODES:
                raise BackendError("RIFE mode is invalid.")
            if self._job_setting("rife_mode", self.rife_mode) == "Multiplier":
                if self._job_setting("rife_multiplier", self.rife_multiplier) not in {f"{x}X" for x in RIFE_MULTIPLIERS}:
                    raise BackendError("RIFE interpolation must be 2X, 3X, 4X, 6X, 8X, or 10X.")
            else:
                if float(self._job_setting("rife_target_fps", self.rife_target_fps)) < 1.0:
                    raise BackendError("Target RIFE FPS must be at least 1 FPS.")
            if self._selected_encode_backend() not in ENCODE_BACKENDS:
                raise BackendError("Final encoding backend is invalid.")
            if self._selected_encode_quality() not in (
                NVENC_QUALITY_PRESETS if self._selected_encode_backend() == "NVIDIA NVENC (fast)" else X265_QUALITY_PRESETS
            ):
                raise BackendError("Final encoding quality is invalid.")
            if self._selected_encode_backend() == "libx265 CPU (best compression)":
                threads = self._selected_x265_threads()
                if threads < 1 or threads > max(1, int(os.cpu_count() or 1)):
                    raise BackendError("libx265 CPU core count is invalid.")

            for queued in self.jobs:
                if self._job_settings_call(queued, self._selected_downscale_enable):
                    self._job_settings_call(queued, self._selected_downscale_factor, strict=True)

            needs_seed = any(
                self._job_settings_call(j, self._selected_upscale_enable)
                and self._job_settings_call(j, self._selected_engine) == "SeedVR2"
                for j in self.jobs
            )
            for queued in self.jobs:
                self._job_settings_call(queued, self._four_scaling_plan, queued.info)
            if needs_seed:
                self._load_api_workflow()
                root = Path(self.comfy_root.get().strip())
                if not (root / "python_embeded" / "python.exe").is_file():
                    raise BackendError("ComfyUI python_embeded\\python.exe was not found.")

            needs_rife = False
            if self._job_setting("rife_enable", self.rife_enable):
                for j in self.jobs:
                    ai_fps, _m, _v, _applied = self._fps_reduction_plan(j.info)
                    use_rife, _mult, _out_fps = self._rife_plan_for_fps(ai_fps)
                    if use_rife:
                        needs_rife = True
                        break
            if needs_rife:
                self._require_tool(self.vspipe.get(), "VapourSynth vspipe")
                model_path = self.rife_model_path.get().strip()
                if not (
                    model_path
                    and (Path(model_path) / "flownet.param").is_file()
                    and (Path(model_path) / "flownet.bin").is_file()
                ):
                    raise BackendError("RIFE model folder is missing or incomplete. Expected flownet.param and flownet.bin.")
                ok, detail = self._vapoursynth_probe(execute_rife=False)
                if not ok:
                    raise BackendError("RIFE plugin is not ready: " + detail)
                src_ok, src_detail = self._vapoursynth_source_probe()
                if not src_ok:
                    raise BackendError("VapourSynth video source plugin is not ready: " + src_detail)
            return True
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))
            return False

    def _validate_workflow_button(self):
        try:
            wf = self._load_api_workflow()
            seed_nodes = [f"{nid}:{n.get('class_type')}" for nid, n in wf.items() if "seedvr2" in str(n.get("class_type", "")).lower()]
            messagebox.showinfo(APP_NAME, f"API workflow is valid.\nNodes: {len(wf)}\nSeedVR2 nodes found: {len(seed_nodes)}\n" + "\n".join(seed_nodes[:8]))
        except Exception as e:
            messagebox.showerror(APP_NAME, str(e))

    def _job_dirs(self, job: Job) -> Tuple[Path, Path, Path, Path]:
        base = self._queue_first_original_parent()
        if base is None:
            original = Path(job.original_path) if job.original_path else Path(job.info.path)
            base = original.parent
        final_root = self._v263_resolve_output_root(base)
        return final_root, final_root / "video Repaired", final_root / "logs", final_root / "Temp"

    def _final_output_path(
        self,
        job: Job,
        final_root: Path,
        actual_geometry: Optional[Tuple[int, int]] = None,
    ) -> Path:
        ext = ".mp4"
        w, h, fps, factor = self._output_geometry(job.info)
        if actual_geometry is not None:
            actual_w, actual_h = map(int, actual_geometry)
            if actual_w <= 0 or actual_h <= 0:
                raise BackendError(f"Invalid output geometry for filename: {actual_geometry}")
            w, h = actual_w, actual_h
        ai_fps, _rm, _rv, _reduced = self._fps_reduction_plan(job.info)
        if ai_fps <= 0 and job.ai_info is not None and job.ai_info.fps > 0:
            ai_fps = float(job.ai_info.fps)
        use_rife, actual_rife_mult, actual_rife_fps = self._rife_plan_for_fps(ai_fps)
        if self._selected_rife_enable() and self._selected_rife_mode() == "Target FPS":
            selected_target = float(self._selected_rife_target_fps())
            if selected_target > 0:
                actual_rife_fps = selected_target
        display_fps = float(actual_rife_fps if use_rife else ai_fps if ai_fps > 0 else fps)
        if display_fps <= 0 and job.info.fps > 0:
            display_fps = float(job.info.fps)
        if display_fps <= 0:
            display_fps = 30.0
        if (
            self._selected_rife_enable()
            and self._selected_rife_mode() == "Target FPS"
            and actual_rife_fps > 0
        ):
            rife_tag = f"_RIFETarget_{self._fmt_fps(actual_rife_fps).replace('.', 'p')}fps"
        else:
            rife_tag = f"_RIFE{actual_rife_mult}x_{self._fmt_fps(actual_rife_fps).replace('.', 'p')}fps" if use_rife else ""
        exact_tag = "_EXACT" if self._needs_exact_resize(job.info) else ""
        engine = self._selected_engine()
        choice = self._selected_upscale_choice(engine)
        stage_tokens = []
        if bool(self._job_setting("scaling_enable", self.scaling_enable)):
            for i in (1, 2, 3, 4):
                active = bool(self._job_setting(f"scaling{i}_enabled", getattr(self, f"scaling{i}_enabled")))
                if not active:
                    stage_tokens.append(f"S{i}OFF")
                else:
                    name = str(self._job_setting(f"scaling{i}_method", getattr(self, f"scaling{i}_method")))
                    tag = ("SeedVR2" if name == "SeedVR2 restoration" else
                           "BasicVSR" if name.startswith("BasicVSR++") else
                           "RealBasicVSR" if name.startswith("RealBasicVSR") else "Bicubic")
                    stage_tokens.append(f"S{i}{tag}")
        processing_tag = ("_" + "_".join(stage_tokens)) if stage_tokens else ""
        if abs(factor - 1.0) > 1e-7:
            processing_tag += f"_{self._format_scale_factor_value(factor)}X"
        down_tag = (
            f"_Down{self._selected_downscale_factor():g}X".replace(".", "p")
            if self._selected_downscale_enable() else ""
        )
        original_stem = self._safe_stem(job.info.path.stem)
        descriptive_suffix = f"{down_tag}{processing_tag}_{w}x{h}{exact_tag}_{self._fmt_fps(display_fps).replace('.', 'p')}fps{rife_tag}{ext}"
        long_name = original_stem + descriptive_suffix
        name = self._v263_safe_component(
            final_root, original_stem, descriptive_suffix,
            identity=str(job.info.path) + ':' + long_name,
            max_full_length=238, max_component_length=210,
        )
        if name != long_name:
            self._post(
                'log', f'V263 WINDOWS PATH GUARD: shortened generated output filename '
                f'({len(long_name)} -> {len(name)} characters) to keep complete path '
                f'under 238 characters. Original video filename remains unchanged. '
                f'SHA256 filename suffix prevents truncation collisions: {name}'
            )
        return final_root / name

    def _write_error_log(self, job: Job, exc: Exception):
        try:
            _, _, logs, _ = self._job_dirs(job)
            logs.mkdir(parents=True, exist_ok=True)
            stamp = f"{_dt.datetime.now():%Y%m%d_%H%M%S}"
            error_name = self._v263_safe_component(
                logs, 'ERROR_' + self._safe_stem(job.info.path.stem), f"_{stamp}.log",
                identity=str(job.info.path) + ':error', max_full_length=235,
                max_component_length=190,
            )
            p = logs / error_name
            p.write_text(f"File: {job.info.path}\nTime: {_dt.datetime.now()}\nStage: {job.stage}\nError: {exc}\n", encoding="utf-8")
        except Exception:
            pass

    def _auto_detect_paths(self):



        for var, name in ((self.ffmpeg, "ffmpeg.exe"), (self.ffprobe, "ffprobe.exe"), (self.vspipe, "vspipe.exe")):
            cur = var.get().strip()
            if cur and (Path(cur).is_file() or shutil.which(cur)):
                continue
            found = shutil.which(name) or shutil.which(name[:-4])
            if found:
                var.set(found)

        if self.vspipe.get() in ("vspipe", ""):
            for p in [
                Path(r"C:\Program Files\VapourSynth\vspipe.exe"),
                Path(r"C:\Program Files\VapourSynth\core64\vspipe.exe"),
                Path(r"C:\Program Files\VapourSynth\core\vspipe.exe"),
            ]:
                if p.is_file():
                    self.vspipe.set(str(p)); break

        if not self.workflow_json.get().strip():
            root = Path(self.comfy_root.get().strip())
            wfroot = root / "ComfyUI" / "user" / "default" / "workflows"
            if wfroot.is_dir():
                candidates = sorted([p for p in wfroot.rglob("*.json") if "seed" in p.name.lower()], key=lambda p: p.stat().st_mtime, reverse=True)
                if candidates:
                    self.workflow_json.set(str(candidates[0]))

    def _settings_variables(self):
        return {
            "input_mode": self.input_mode, "input_path": self.input_path, "output_parent": self.output_parent,
            "recursive": self.recursive,
            "move_processed_enable": self.move_processed_enable,
            "move_success_folder": self.move_success_folder,
            "move_failed_folder": self.move_failed_folder,
            "fps_reduce_enable": self.fps_reduce_enable,
            "fps_reduce_mode": self.fps_reduce_mode,
            "fps_reduce_max": self.fps_reduce_max,
            "enhancement_enable": self.enhancement_enable,
            "repair_enable": self.repair_enable, "deinterlace_auto": self.deinterlace_auto, "denoise": self.denoise,
            "color_correction": self.color_correction, "brightness_correction": self.brightness_correction,
            "white_correction": self.white_correction,
            "sharpen": self.sharpen, "deband": self.deband,
            "scaling_enable": self.scaling_enable,
            "scaling1_enabled": self.scaling1_enabled,
            "scaling1_method": self.scaling1_method,
            "scaling1_factor": self.scaling1_factor,
            "scaling1_target": self.scaling1_target,
            "scaling2_enabled": self.scaling2_enabled,
            "scaling2_method": self.scaling2_method,
            "scaling2_factor": self.scaling2_factor,
            "scaling2_target": self.scaling2_target,
            "scaling3_enabled": self.scaling3_enabled,
            "scaling3_method": self.scaling3_method,
            "scaling3_factor": self.scaling3_factor,
            "scaling3_target": self.scaling3_target,
            "scaling4_target": self.scaling4_target,
            "upscale_engine": self.upscale_engine,
            "upscale_enable": self.upscale_enable,
            "downscale_enable": self.downscale_enable,
            "downscale_preset": self.downscale_preset,
            "downscale_custom": self.downscale_custom,
            "seed_upscale": self.seed_upscale,
            "seedvr2_custom_factor": self.seedvr2_custom_factor,
            "seed_target_resolution": self.seed_target_resolution,
            "seed_parameter_mode": self.seed_parameter_mode,
            "seed_batch_max": self.seed_batch_max,
            "seed_temporal_overlap": self.seed_temporal_overlap,
            "seed_vae_tile": self.seed_vae_tile,
            "seed_vae_spatial_overlap": self.seed_vae_spatial_overlap,
            "comfy_disable_dynamic_vram": self.comfy_disable_dynamic_vram,
            "comfy_disable_async_offload": self.comfy_disable_async_offload,
            "preseed_mode": self.preseed_mode,
            "preseed_resolution": self.preseed_resolution,
            "native_sr_enable": self.native_sr_enable,
            "native_sr_model": self.native_sr_model,
            "native_sr_python": self.native_sr_python,
            "native_sr_repo": self.native_sr_repo,
            "native_sr_config": self.native_sr_config,
            "native_sr_checkpoint": self.native_sr_checkpoint,
            "native_sr_max_seq_len": self.native_sr_max_seq_len,
            "native_sr_chunk_frames": self.native_sr_chunk_frames,
            "basicvsr_persistent_worker": self.basicvsr_persistent_worker,
            "basicvsr_tile_profile": self.basicvsr_tile_profile,
            "pre_neural_downscale_preset": self.pre_neural_downscale_preset,
            "pre_neural_downscale_custom": self.pre_neural_downscale_custom,
            "native_sr_preseed_preset": self.native_sr_preseed_preset,
            "native_sr_preseed_custom": self.native_sr_preseed_custom,
            "force_exact_resolution": self.force_exact_resolution,
            "rife_enable": self.rife_enable, "rife_mode": self.rife_mode,
            "rife_multiplier": self.rife_multiplier, "rife_target_fps": self.rife_target_fps,
            "rife_gpu_thread": self.rife_gpu_thread,
            "encode_backend": self.encode_backend, "encode_quality": self.encode_quality,
            "x265_threads": self.x265_threads, "install_root": self.install_root,
            "ffmpeg": self.ffmpeg, "ffprobe": self.ffprobe,
            "comfy_root": self.comfy_root, "comfy_launch_mode": self.comfy_launch_mode,
            "workflow_json": self.workflow_json, "comfy_port": self.comfy_port,
            "vspipe": self.vspipe, "rife_plugin_dir": self.rife_plugin_dir, "rife_plugin_dll": self.rife_plugin_dll,
            "rife_model_path": self.rife_model_path, "vs_source_plugin_dll": self.vs_source_plugin_dll,
        }

    def _install_autosave_traces(self):
        for var in self._settings_variables().values():
            try:
                var.trace_add("write", lambda *_: self._schedule_save_settings())
            except Exception:
                pass

    def _schedule_save_settings(self):
        if not self._autosave_ready:
            return
        if self._autosave_after_id is not None:
            try:
                self.after_cancel(self._autosave_after_id)
            except Exception:
                pass
        self._autosave_after_id = self.after(500, lambda: self._save_settings(silent=True))

    def _save_settings(self, silent=False):
        data = {k: v.get() for k, v in self._settings_variables().items()}
        data["v243_seed_preset_migrated"] = True
        try:
            self.settings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            self._autosave_after_id = None
            if not silent:
                self._log(f"Settings saved: {self.settings_path}")
        except Exception as e:
            if not silent:
                messagebox.showerror(APP_NAME, f"Could not save settings: {e}")

    def _load_settings(self):


        source = self.settings_path
        if not source.is_file():
            for previous_name in (
                'Upscaler_V215_settings.json', 'Upscaler_V214_settings.json', 'Upscaler_V213_settings.json', 'Upscaler_V212_settings.json', 'Upscaler_V211_settings.json', 'Upscaler_V210_settings.json', 'Upscaler_V209_settings.json', 'Upscaler_V208_settings.json', 'Upscaler_V207_settings.json', 'Upscaler_V206_settings.json', 'Upscaler_V205_settings.json', 'Upscaler_V204_settings.json', 'Upscaler_V203_settings.json', 'Upscaler_V202_settings.json', 'Upscaler_V201_settings.json', 'Upscaler_V200_settings.json', 'Upscaler_V199_settings.json', 'Upscaler_V198_settings.json', 'Upscaler_V197_settings.json', 'Upscaler_V196_settings.json', 'Upscaler_V195_settings.json', 'Upscaler_V194_settings.json', 'Upscaler_V193_settings.json', 'Upscaler_V192_settings.json', 'Upscaler_V191_settings.json', 'Upscaler_V190_settings.json', 'Upscaler_V189_settings.json', 'Upscaler_V188_settings.json', 'Upscaler_V187_settings.json', 'Upscaler_V186_settings.json', 'Upscaler_V185_settings.json', 'Upscaler_V184_settings.json', 'Upscaler_V183_settings.json', 'Upscaler_V182_settings.json', 'Upscaler_V181_settings.json', 'Upscaler_V180_settings.json', 'Upscaler_V179_settings.json', 'Upscaler_V178_settings.json', 'Upscaler_V177_settings.json', 'Upscaler_V176_settings.json', 'Upscaler_V175_settings.json', 'Upscaler_V174_settings.json', 'Upscaler_V173_settings.json', 'Upscaler_V172_settings.json', 'Upscaler_V171_settings.json', 'Upscaler_V170_settings.json', 'Upscaler_V169_settings.json', 'Upscaler_V168_settings.json', 'Upscaler_V167_settings.json', 'Upscaler_V166_settings.json', 'Upscaler_V165_settings.json', 'Upscaler_V164_settings.json', 'Upscaler_V163_settings.json', 'Upscaler_V162_settings.json', 'Upscaler_V161_settings.json', 'Upscaler_V160_settings.json', 'Upscaler_V159_settings.json', 'Upscaler_V158_settings.json', 'Upscaler_V157_settings.json', 'Upscaler_V156_settings.json', 'Upscaler_V155_settings.json', 'Upscaler_V154_settings.json', 'Upscaler_V153_settings.json', 'Upscaler_V152_settings.json', 'Upscaler_V151_settings.json', 'Upscaler_V150_settings.json', 'Upscaler_V149_settings.json', 'Upscaler_V148_settings.json', 'Upscaler_V147_settings.json', 'Upscaler_V146_settings.json', 'Upscaler_V145_settings.json', 'Upscaler_V144_settings.json', 'Upscaler_V143_settings.json', 'Upscaler_V142_settings.json', 'Upscaler_V141_settings.json', 'Upscaler_V140_settings.json', 'Upscaler_V139_settings.json', 'Upscaler_V138_settings.json', 'Upscaler_V137_settings.json', 'Upscaler_V136_settings.json', 'Upscaler_V135_settings.json', 'Upscaler_V134_settings.json', 'Upscaler_V133_settings.json', 'Upscaler_V132_settings.json', 'Upscaler_V131_settings.json', 'Upscaler_V130_settings.json', 'Upscaler_V129_settings.json', 'Upscaler_V128_settings.json', 'Upscaler_V127_settings.json', 'Upscaler_V126_settings.json', 'Upscaler_V125_settings.json', 'Upscaler_V124_settings.json', 'Upscaler_V123_settings.json', 'Upscaler_V122_settings.json', 'Upscaler_V121_settings.json', 'Upscaler_V120_settings.json', 'Upscaler_V119_settings.json', 'Upscaler_V118_settings.json', 'Upscaler_V117_settings.json', 'Upscaler_V116_settings.json', 'Upscaler_V115_settings.json', 'Upscaler_V114_settings.json', 'Upscaler_V113_settings.json', 'Upscaler_V112_settings.json', 'Upscaler_V111_settings.json', 'Upscaler_V110_settings.json', 'Upscaler_V109_settings.json', 'Upscaler_V108_settings.json', 'Upscaler_V107_settings.json', 'Upscaler_V106_settings.json', 'Upscaler_V105_settings.json', 'Upscaler_V104_settings.json',
                'Upscaler_V103_settings.json', 'Upscaler_V102_settings.json', 'Upscaler_V101_settings.json', 'Upscaler_V100_settings.json', 'Upscaler_V99_settings.json', 'Upscaler_V98_settings.json', 'Upscaler_V97_settings.json', 'Upscaler_V96_settings.json', 'Upscaler_V95_settings.json', 'Upscaler_V94_settings.json', 'Upscaler_V93_settings.json', 'Upscaler_V92_settings.json', 'Upscaler_V91_settings.json', 'Upscaler_V90_settings.json', 'Upscaler_V89_settings.json', 'Upscaler_V88_settings.json', 'Upscaler_V87_settings.json', 'Upscaler_V86_settings.json', 'Upscaler_V85_settings.json', 'Upscaler_V84_settings.json', 'Upscaler_V83_settings.json', 'Upscaler_V82_settings.json', 'Upscaler_V81_settings.json', 'Upscaler_V80_settings.json', 'Upscaler_V79_settings.json', 'Upscaler_V78_settings.json', 'Upscaler_V77_settings.json', 'Upscaler_V76_settings.json', 'Upscaler_V75_settings.json', 'Upscaler_V74_settings.json', 'Upscaler_V73_settings.json', 'Upscaler_V72_settings.json', 'Upscaler_V71_settings.json', 'Upscaler_V70_settings.json', 'Upscaler_V69_settings.json', 'Upscaler_V68_settings.json', 'Upscaler_V67_settings.json', 'Upscaler_V66_settings.json', 'Upscaler_V65_settings.json', 'Upscaler_V64_settings.json', 'Upscaler_V63_settings.json', 'Upscaler_V62_settings.json', 'Upscaler_V61_settings.json', 'Upscaler_V60_settings.json', 'Upscaler_V59_settings.json', 'Upscaler_V58_settings.json', 'Upscaler_V57_settings.json', 'Upscaler_V56_settings.json', 'Upscaler_V55_settings.json', 'Upscaler_V54_settings.json', 'Upscaler_V53_settings.json', 'Upscaler_V52_settings.json', 'Upscaler_V51_settings.json', 'Upscaler_V50_settings.json', 'Upscaler_V49_settings.json', 'Upscaler_V48_settings.json', 'Upscaler_V47_settings.json', 'Upscaler_V46_settings.json', 'Upscaler_V45_settings.json', 'Upscaler_V44_settings.json', 'Upscaler_V43_settings.json', 'Upscaler_V42_settings.json', 'Upscaler_V41_settings.json', 'Upscaler_V40_settings.json', 'Upscaler_V39_settings.json', 'Upscaler_V38_settings.json', 'Upscaler_V37_settings.json', 'Upscaler_V36_settings.json', 'Upscaler_V35_settings.json', 'Upscaler_V34_settings.json', 'Upscaler_V33_settings.json', 'Upscaler_V32_settings.json', 'Upscaler_V31_settings.json', 'Upscaler_V30_settings.json', 'Upscaler_V29_settings.json', 'Upscaler_V28_settings.json', 'Upscaler_V27_settings.json', 'Upscaler_V26_settings.json', 'Upscaler_V25_settings.json', 'Upscaler_V24_settings.json', 'Upscaler_V23_settings.json', 'Upscaler_V22_settings.json', 'Upscaler_V21_settings.json', 'Upscaler_V20_settings.json', 'Upscaler_V19_settings.json', 'Upscaler_V18_settings.json',
                'Upscaler_V17_settings.json', 'Upscaler_V16_settings.json', 'Upscaler_V15_settings.json',
                'Upscaler_V14_settings.json', 'Upscaler_V13_settings.json', 'Upscaler_V12_settings.json',
                'Upscaler_V11_settings.json', 'Upscaler_V10_settings.json', 'Upscaler_V9_settings.json',
                'Upscaler_V8_settings.json', 'Upscaler_V7_settings.json', 'Upscaler_V6_settings.json',
                'Upscaler_V5_settings.json', 'Upscaler_V4_settings.json', 'Upscaler_V3_settings.json',
                'Upscaler_V2_settings.json', 'Upscaler_V1_settings.json'
            ):
                previous = self.script_dir / previous_name
                if previous.is_file():
                    source = previous
                    break
            else:
                return
        try:
            data = json.loads(source.read_text(encoding="utf-8"))
            self._v243_seed_preset_migrated = bool(data.get("v243_seed_preset_migrated", False))
            mapping = self._settings_variables()
            for k, v in mapping.items():
                if k in data:
                    v.set(data[k])


            # V241 migration from V240: preserve previous selected neural engine
            # and VSR pre-SeedVR2 factor; disable old pre-AI Lanczos stage.
            self.downscale_enable.set(False)
            if "preseed_mode" not in data:
                if bool(data.get("native_sr_enable", False)):
                    model = str(data.get("native_sr_model", "RealBasicVSR_x4"))
                    self.preseed_mode.set("BasicVSR++&Bicubic" if model == "BasicVSRPlusPlus_x4" else "RealBasicVSR&Bicubic")
                else:
                    self.preseed_mode.set("Only Bicubic")
            if "preseed_resolution" not in data:
                self.preseed_resolution.set("Factor")


            if "native_sr_preseed_preset" not in data:
                former_scale = str(data.get("seed_upscale", "4X"))
                if former_scale in ("1X", "1.25X", "1.5X", "1.75X", "2X", "2.5X", "3X", "3.5X", "4X", "4.5X", "5X", "6X", "7X", "8X", "10X", "12X"):
                    self.native_sr_preseed_preset.set(former_scale)
                else:
                    try:
                        number = float(former_scale.rstrip("xX"))
                        if 1.0 <= number <= 12.0 and math.isfinite(number):
                            self.native_sr_preseed_custom.set(f"{number:g}")
                    except (ValueError, OverflowError):
                        pass

            legacy_choice = str(data.get("upscale", ""))
            legacy_engine = str(data.get("upscale_engine", self._job_setting("upscale_engine", self.upscale_engine)))
            if "seed_upscale" not in data and legacy_engine == "SeedVR2" and legacy_choice in SEED_UPSCALE_CHOICES:
                self.seed_upscale.set(legacy_choice)


            for enhancement_var in (
                self.denoise,
                self.color_correction,
                self.brightness_correction,
                self.white_correction,
            ):
                if enhancement_var.get() not in ENHANCEMENT_STATES:
                    enhancement_var.set("Auto" if str(enhancement_var.get()).strip().lower() != "off" else "Off")

            if self.sharpen.get() not in {"Off", "Low", "Medium", "High"}:
                self.sharpen.set("Off")
            if self.deband.get() not in {"Off", "Low", "Medium", "High"}:
                self.deband.set("Off")


            if self._job_setting("seed_upscale", self.seed_upscale) not in SEED_UPSCALE_CHOICES:
                legacy_seed_choice = str(self._job_setting("seed_upscale", self.seed_upscale))
                if legacy_seed_choice == "OFF":
                    self.upscale_enable.set(False)
                if legacy_seed_choice == "1444p":
                    legacy_seed_choice = "1440p"
                if legacy_seed_choice in TARGET_HEIGHTS:
                    self.seed_target_resolution.set(legacy_seed_choice)
                self.seed_upscale.set("2X")
            if self._job_setting("seed_target_resolution", self.seed_target_resolution) not in SEED_TARGET_RESOLUTIONS:
                self.seed_target_resolution.set("Use upscale factor")
            self.fps_reduce_mode.set("Maximum FPS")
            try:
                current_fps_max = float(self.fps_reduce_max.get())
            except Exception:
                current_fps_max = 30.0
            allowed_fps_max = [float(x) for x in FPS_MAX_FOR_AI_CHOICES]
            self.fps_reduce_max.set(min(allowed_fps_max, key=lambda x: abs(x - current_fps_max)))
            if self._job_setting("rife_mode", self.rife_mode) not in RIFE_MODES:
                self.rife_mode.set("Multiplier")
            if self._job_setting("rife_multiplier", self.rife_multiplier) not in {f"{x}X" for x in RIFE_MULTIPLIERS}:
                self.rife_multiplier.set("2X")
            try:
                if float(self._job_setting("rife_target_fps", self.rife_target_fps)) < 1.0:
                    self.rife_target_fps.set(50.0)
            except Exception:
                self.rife_target_fps.set(50.0)


            if self._job_setting("upscale_engine", self.upscale_engine) not in UPSCALE_ENGINES:
                self.upscale_engine.set("SeedVR2")
            if self._job_setting("comfy_launch_mode", self.comfy_launch_mode) not in ("Standard NVIDIA", "NVIDIA Fast"):
                self.comfy_launch_mode.set("NVIDIA Fast")
            success_raw = str(self.move_success_folder.get()).strip()
            failed_raw = str(self.move_failed_folder.get()).strip()
            legacy_success_names = {
                "", "upscal done", "originaldone", "originalmoviesupscalesuccess"
            }
            legacy_failed_names = {
                "", "upscal failled", "originalfailled", "originalmoviesupscalefailled"
            }
            if Path(success_raw).name.casefold() in legacy_success_names:
                self.move_success_folder.set(DEFAULT_SUCCESS_FOLDER)
            if Path(failed_raw).name.casefold() in legacy_failed_names:
                self.move_failed_folder.set(DEFAULT_FAILED_FOLDER)
            self.output_parent.set("")
        except Exception:
            pass

    def _selected_upscale_enable(self) -> bool:
        """SeedVR2 is active only when selected in an enabled scaling stage."""
        if not bool(self._job_setting("scaling_enable", self.scaling_enable)):
            return False
        return any(
            bool(self._job_setting(f"scaling{i}_enabled", getattr(self, f"scaling{i}_enabled"))) and
            str(self._job_setting(f"scaling{i}_method", getattr(self, f"scaling{i}_method"))) == "SeedVR2 restoration"
            for i in (1, 2, 3, 4)
        )

    def _sync_upscale_size_choice_from_controls(self) -> None:
        self.upscale_size_choice.set("1X")


    def _on_upscale_size_choice_changed(self, _event=None) -> None:
        return


    def _toggle_upscale_enable(self):
        self.upscale_enable.set(not bool(self._raw_tk_value(self.upscale_enable)))
        self._update_upscale_controls()

    def _update_upscale_controls(self):
        active = bool(self._raw_tk_value(self.upscale_enable))
        if hasattr(self, "upscale_toggle_button"):
            self.upscale_toggle_button.configure(text="RESTORATION ON" if active else "RESTORATION OFF",
                bg="#2E8B57" if active else "#D9D9D9", fg="white" if active else "#555555")
        if hasattr(self, "scaling_boxes"):
            self._update_scaling_widgets()
        self._guarded_section2_refresh_preview()


    def _update_controls(self):
        self.rec_check.configure(state="normal" if self.input_mode.get() == "folder" else "disabled")
        self._update_move_processed_controls()
        self._update_upscale_controls()
        self._update_downscale_controls()
        self._update_fps_reduce_controls()
        self._update_rife_controls()
        self._update_encode_controls()

    def _open_output_folder(self):
        p = self._dynamic_output_root()
        if p is None:
            raw = str(self.input_path.get() or "").strip()
            if not raw:
                return
            first = raw.split(" | ", 1)[0].strip()
            base = Path(first)
            if base.is_file():
                base = base.parent
            p = self._v263_resolve_output_root(base)

        p.mkdir(parents=True, exist_ok=True)
        self._log(f"V137 OUTPUT FOLDER: opening {p}")
        if os.name == "nt":
            os.startfile(str(p))


    def _wait_if_paused(self) -> float:
        if not self.pause_event.is_set():
            return 0.0
        t0 = time.time()
        while self.pause_event.is_set():
            if self.stop_event.is_set():
                raise Cancelled()
            time.sleep(0.10)
        return max(0.0, time.time() - t0)

    def _active_pause_root_pids(self) -> List[int]:
        roots: List[int] = []
        proc = self.comfy_proc
        if proc is not None and proc.poll() is None:
            roots.append(int(proc.pid))
        with self.process_lock:
            candidates = [self.current_process] + list(self._aux_processes)
        for p in candidates:
            if p is not None and p.poll() is None:
                roots.append(int(p.pid))

        return list(dict.fromkeys(pid for pid in roots if pid > 0))

    def _pause_queue(self):
        if not (self.worker and self.worker.is_alive()):
            return
        if self.pause_event.is_set():
            return


        self.pause_event.set()
        self._pre_pause_step_text = self.current_step_text.get()
        self._pre_pause_eta_text = self.eta_text.get()
        self._pause_started_at = time.time()

        try:
            roots = self._active_pause_root_pids()
            suspended = self._suspend_process_trees(roots) if roots else []
            self._paused_process_pids = suspended
        except Exception as e:


            try:
                self._resume_pid_list(self._paused_process_pids)
            except Exception:
                pass
            self._paused_process_pids = []
            self._pause_started_at = None
            self.pause_event.clear()
            self.pause_btn.configure(state="normal", text="PAUSE", style="Pause.TButton")
            self._set_processing_highlight("processing")
            self.resume_btn.configure(state="disabled")
            messagebox.showerror(APP_NAME, f"Could not pause the active computation safely:\n\n{e}")
            return

        if 0 <= self.current_job_index < len(self.jobs):
            self._refresh_job_elapsed_display(
                self.jobs[self.current_job_index],
                force=True,
                update_row=True,
            )

        self.start_btn.configure(style="Start.TButton")
        self.pause_btn.configure(state="disabled", text="PAUSED", style="Pause.TButton")
        self._set_processing_highlight("paused")
        self.resume_btn.configure(state="normal")
        self.save_exit_btn.configure(state="disabled")
        self.current_step_text.set("Current step: PAUSED - computation state preserved")
        self.eta_text.set("ETA: PAUSED")
        self._log(
            f"PAUSE V101: computation suspended in place; {len(self._paused_process_pids)} process(es) suspended. "
            "CUDA/model state and VRAM allocations are intentionally retained. Temporary files are not deleted."
        )

    def _resume_queue(self):
        if not self.pause_event.is_set():
            return

        paused_for = 0.0
        if self._pause_started_at is not None:
            paused_for = max(0.0, time.time() - self._pause_started_at)

        try:
            self._resume_pid_list(self._paused_process_pids)
        except Exception as e:
            messagebox.showerror(
                APP_NAME,
                f"Resume encountered a Windows process error:\n\n{e}\n\n"
                "The queue has not been intentionally stopped. You can try RESUME again or use STOP."
            )
            return

        self._paused_process_pids = []
        self._pause_started_at = None
        self._resume_serial += 1


        if 0 <= self.current_job_index < len(self.jobs):
            j = self.jobs[self.current_job_index]
            if j.started_at > 0:
                j.started_at += paused_for

        self.pause_event.clear()

        if 0 <= self.current_job_index < len(self.jobs):
            self._refresh_job_elapsed_display(
                self.jobs[self.current_job_index],
                force=True,
                update_row=True,
            )
        self.pause_btn.configure(state="normal" if self.worker and self.worker.is_alive() else "disabled", text="PAUSE", style="Pause.TButton")
        self._set_processing_highlight("processing" if self.worker and self.worker.is_alive() else "idle")
        self.resume_btn.configure(state="disabled")
        self.save_exit_btn.configure(state="disabled", style="SaveExit.TButton")
        if self._pre_pause_step_text:
            self.current_step_text.set(self._pre_pause_step_text)
        if self._pre_pause_eta_text:
            self.eta_text.set(self._pre_pause_eta_text)
        self._log(f"RESUME V101: computation resumed from the preserved state after {self._fmt_time(paused_for)} paused.")

    def _resume_for_stop(self):
        try:
            self._resume_pid_list(self._paused_process_pids)
        except Exception:
            pass
        self._paused_process_pids = []
        self._pause_started_at = None
        self.pause_event.clear()
        self._set_processing_highlight("idle")

    def _stop_queue(self, confirm: bool = True):
        queue_active = bool(self.worker and self.worker.is_alive())
        if not queue_active:
            return

        if confirm:
            current_name = ""
            if 0 <= self.current_job_index < len(self.jobs):
                current_name = self.jobs[self.current_job_index].info.path.name
            message = (
                "Are you sure you want to STOP the queue?\n\n"
                "The active video process will be terminated. Completed temporary/intermediate files for the current job will be preserved for recovery."
            )
            if current_name:
                message += f"\n\nCurrent file:\n{current_name}"
            if not messagebox.askyesno(APP_NAME, message, icon="warning", default="no"):
                self._log("STOP cancelled by user.")
                return

        self.stop_event.set()
        self._resume_for_stop()
        self.pause_btn.configure(state="disabled", text="PAUSE", style="Pause.TButton")
        self._set_processing_highlight("idle")
        self.resume_btn.configure(state="disabled")
        self.save_exit_btn.configure(state="disabled", style="SaveExit.TButton")
        self.stop_btn.configure(state="disabled")
        self._interrupt_comfy_prompt()
        with self.process_lock:
            p = self.current_process
            aux = list(self._aux_processes)
        if p and p.poll() is None:
            self._terminate_tree(p)
        for ap in aux:
            if ap and ap.poll() is None:
                self._terminate_tree(ap)

        self._stop_managed_comfy(reason="STOP: shutting down the V101-owned ComfyUI backend.", wait_port=True)
        self._cleanup_retained_comfy_inputs()
        self._log("STOP confirmed. Active process is being terminated.")

    def _close_guard_active(self) -> bool:
        if self.worker and self.worker.is_alive():
            return True
        with self.process_lock:
            current = self.current_process
            aux = list(self._aux_processes)
        if current is not None:
            try:
                if current.poll() is None:
                    return True
            except Exception:
                return True
        for proc in aux:
            if proc is None:
                continue
            try:
                if proc.poll() is None:
                    return True
            except Exception:
                return True
        return False

    def _on_alt_f4(self, _event=None):
        self._on_close()
        return "break"

    def _on_close(self):
        if self._close_guard_active():
            self._log("V257: close blocked during active processing. Use STOP first.")
            messagebox.showwarning(APP_NAME, "Processing is active. Click STOP before closing the window.")
            return
        self._resume_for_stop()
        self._save_settings(silent=True)
        self._stop_managed_comfy(reason="Closing SeedVR2 restoration application.", wait_port=False)
        self._cleanup_retained_comfy_inputs()
        self.destroy()



    @staticmethod
    def _parse_rate(s: str) -> float:
        try:
            if "/" in s:
                a, b = s.split("/", 1)
                return float(a) / float(b) if float(b) else 0.0
            return float(s)
        except Exception:
            return 0.0

    @staticmethod
    def _to_int(x) -> int:
        try: return int(float(x))
        except Exception: return 0

    @staticmethod
    def _to_float(x) -> float:
        try: return float(x)
        except Exception: return 0.0

    @staticmethod
    def _round_fps(x: float) -> int:
        try:
            value = float(x)
        except Exception:
            return 0
        if value <= 0:
            return 0
        return max(1, int(math.floor(value + 0.5)))

    @staticmethod
    def _fmt_fps(x: float) -> str:
        value = UpscalerApp._round_fps(x)
        return str(value) if value > 0 else "?"

    @staticmethod
    def _fmt_compact_duration(sec: float, include_seconds_under_minute: bool = True) -> str:
        if sec is None:
            return "--"
        try:
            total = int(round(float(sec)))
        except Exception:
            return "--"
        if total < 0:
            return "--"

        days, rem = divmod(total, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)

        if days:
            return f"{days}d{hours}h{minutes}m"
        if hours:
            return f"{hours}h{minutes}m"
        if minutes:
            return f"{minutes}m"
        if include_seconds_under_minute:
            return f"{seconds}s"
        return "<1m"

    @staticmethod
    def _fmt_elapsed_duration(sec: float) -> str:
        if sec is None:
            return "--"
        try:
            total = max(0, int(float(sec)))
        except Exception:
            return "--"

        if total < 60:
            return "<1m"

        days, rem = divmod(total, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, _seconds = divmod(rem, 60)

        if days:
            return f"{days}d{hours}h{minutes}m"
        if hours:
            return f"{hours}h{minutes}m"
        return f"{minutes}m"

    def _job_elapsed_now(self, job: Job) -> float:
        if job.status in ("Done", "Failed", "Stopped") and job.elapsed_seconds > 0:
            return max(0.0, float(job.elapsed_seconds))

        if job.started_at <= 0:
            return 0.0


        now_point = time.time()
        if (
            self.pause_event.is_set()
            and 0 <= self.current_job_index < len(self.jobs)
            and self.jobs[self.current_job_index] is job
            and self._pause_started_at is not None
        ):
            now_point = float(self._pause_started_at)

        return max(
            0.0,
            now_point
            - float(job.started_at)
            + float(job.pre_run_overhead_seconds or 0.0),
        )

    def _refresh_job_elapsed_display(
        self,
        job: Job,
        force: bool = False,
        update_row: bool = True,
    ) -> bool:
        elapsed = self._job_elapsed_now(job)


        if job.started_at <= 0 and job.status not in ("Done", "Failed", "Stopped"):
            new_text = "--"
            bucket = -1
        else:
            new_text = self._fmt_elapsed_duration(elapsed)
            bucket = int(elapsed // 60)

        changed = (
            force
            or bucket != job.elapsed_display_bucket
            or new_text != job.elapsed_text
        )

        job.elapsed_seconds = elapsed
        if changed:
            job.elapsed_text = new_text
            job.elapsed_display_bucket = bucket
            if update_row:
                self._update_job_row(job)

        return changed

    @staticmethod
    def _fmt_time(sec: float) -> str:
        if sec is None or sec <= 0:
            return "--"
        sec = int(round(sec))
        h, rem = divmod(sec, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

    @staticmethod
    def _safe_stem(s: str) -> str:
        s = re.sub(r'[<>:"/\\|?*]+', "_", s).strip().rstrip(".")
        return s or "video"

    @staticmethod
    def _quote(cmd: List[str]) -> str:
        return " ".join(f'"{x}"' if any(c.isspace() for c in str(x)) else str(x) for x in cmd)

    @staticmethod
    def _no_window() -> int:
        return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    @staticmethod
    def _windows_process_tree(root_pids: List[int]) -> List[Tuple[int, int]]:
        roots = [int(x) for x in root_pids if int(x) > 0]
        if not roots:
            return []
        if os.name != "nt":
            return [(pid, 0) for pid in roots]

        TH32CS_SNAPPROCESS = 0x00000002
        MAX_PATH = 260
        INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = [
                ("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.c_size_t),
                ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", wintypes.LONG),
                ("dwFlags", wintypes.DWORD),
                ("szExeFile", wintypes.WCHAR * MAX_PATH),
            ]

        k32 = ctypes.windll.kernel32
        k32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
        k32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        k32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
        k32.Process32FirstW.restype = wintypes.BOOL
        k32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
        k32.Process32NextW.restype = wintypes.BOOL
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        k32.CloseHandle.restype = wintypes.BOOL
        snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snap == INVALID_HANDLE_VALUE:
            raise OSError("CreateToolhelp32Snapshot failed while preparing Pause.")
        parent: Dict[int, int] = {}
        try:
            entry = PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
            ok = k32.Process32FirstW(snap, ctypes.byref(entry))
            while ok:
                parent[int(entry.th32ProcessID)] = int(entry.th32ParentProcessID)
                ok = k32.Process32NextW(snap, ctypes.byref(entry))
        finally:
            k32.CloseHandle(snap)


        depth: Dict[int, int] = {pid: 0 for pid in roots}
        changed = True
        while changed:
            changed = False
            for pid, ppid in parent.items():
                if ppid in depth and pid not in depth:
                    depth[pid] = depth[ppid] + 1
                    changed = True
        return sorted(depth.items(), key=lambda x: (x[1], x[0]))

    @staticmethod
    def _nt_suspend_resume_pid(pid: int, suspend: bool) -> None:
        if os.name != "nt":
            raise OSError("True process suspension is implemented for Windows only.")
        PROCESS_SUSPEND_RESUME = 0x0800
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        k32 = ctypes.windll.kernel32
        ntdll = ctypes.windll.ntdll
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        k32.CloseHandle.restype = wintypes.BOOL
        fn = ntdll.NtSuspendProcess if suspend else ntdll.NtResumeProcess
        fn.argtypes = [wintypes.HANDLE]
        fn.restype = wintypes.LONG
        handle = k32.OpenProcess(PROCESS_SUSPEND_RESUME | PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not handle:


            err = int(k32.GetLastError())
            if err == 87:
                return
            raise OSError(f"OpenProcess failed for PID {pid} (Windows error {err}).")
        try:
            status = int(fn(handle))
            if status != 0:
                raise OSError(
                    f"{'NtSuspendProcess' if suspend else 'NtResumeProcess'} failed for PID {pid} "
                    f"with NTSTATUS 0x{status & 0xFFFFFFFF:08X}."
                )
        finally:
            k32.CloseHandle(handle)

    @classmethod
    def _suspend_process_trees(cls, root_pids: List[int]) -> List[int]:
        tree = cls._windows_process_tree(root_pids)
        if not tree:
            return []
        suspended: List[int] = []
        try:


            for pid, _depth in tree:
                cls._nt_suspend_resume_pid(pid, True)
                suspended.append(pid)
            return suspended
        except Exception:
            for pid in reversed(suspended):
                try:
                    cls._nt_suspend_resume_pid(pid, False)
                except Exception:
                    pass
            raise

    @classmethod
    def _resume_pid_list(cls, pids: List[int]) -> None:


        errors: List[str] = []
        for pid in reversed(list(dict.fromkeys(int(x) for x in pids if int(x) > 0))):
            try:
                cls._nt_suspend_resume_pid(pid, False)
            except Exception as e:
                errors.append(str(e))
        if errors:
            raise OSError("; ".join(errors[:4]))

    @staticmethod
    def _terminate_tree(proc: subprocess.Popen):
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            try: proc.kill()
            except Exception: pass

    @staticmethod
    def _tool(value: str) -> str:
        value = value.strip()
        return str(Path(value)) if Path(value).is_file() else value

    @staticmethod
    def _require_tool(value: str, label: str):
        value = value.strip()
        if Path(value).is_file() or shutil.which(value):
            return
        raise BackendError(f"{label} was not found: {value}")



def _hide_windows_console_window() -> bool:
    if os.name != "nt":
        return False
    try:
        k32 = ctypes.windll.kernel32
        u32 = ctypes.windll.user32
        k32.GetConsoleWindow.argtypes = []
        k32.GetConsoleWindow.restype = wintypes.HWND
        u32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        u32.ShowWindow.restype = wintypes.BOOL
        hwnd = k32.GetConsoleWindow()
        if not hwnd:
            return False
        u32.ShowWindow(hwnd, 0)
        return True
    except Exception:
        return False


def _relaunch_with_pythonw() -> bool:
    if os.name != "nt":
        return False
    if os.environ.get("UPSCALER_V101_PYTHONW") == "1":
        _hide_windows_console_window()
        return False

    current_exe = Path(sys.executable)
    if current_exe.name.lower() in {"pythonw.exe", "pythonw"}:
        _hide_windows_console_window()
        return False

    candidates = [
        current_exe.with_name("pythonw.exe"),
        Path(sys.base_prefix) / "pythonw.exe",
        Path(sys.prefix) / "pythonw.exe",
    ]
    pythonw = next((candidate for candidate in candidates if candidate.is_file()), None)
    if pythonw is None:
        _hide_windows_console_window()
        return False

    script = Path(sys.argv[0]).resolve()
    if not script.is_file():
        _hide_windows_console_window()
        return False

    env = os.environ.copy()
    env["UPSCALER_V101_PYTHONW"] = "1"
    creationflags = 0
    creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
    creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)

    try:
        subprocess.Popen(
            [str(pythonw), str(script), *sys.argv[1:]],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            creationflags=creationflags,
            env=env,
            cwd=str(Path.cwd()),
        )
        return True
    except Exception:
        _hide_windows_console_window()
        return False


if __name__ == "__main__":
    if _relaunch_with_pythonw():
        sys.exit(0)
    _hide_windows_console_window()
    app = UpscalerApp()
    app.mainloop()
