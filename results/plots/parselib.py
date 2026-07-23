import json
import os
import pandas as pd

class Filter:
    def __init__(self):
        self.app_buffer: str = None
        self.adapter_type: str = None
        self.rate: int = None
        self.sysctl_cmd: str = None
        self.cca: str = None
        self.json: bool = None
        self.kernel: str = None
        self.loss_mode: str = None
        self.n: int = None
        self.parallel: int = None
        self.delay_rtt: int = None
        self.timestamp: str = None
        self.test_cca: str = None
        self.bdp: int = None
        self.tso: str = None
        self.hostq: str = None
        self.bandwidth_delay_product: int = None
        self.default_qdisc: str = None
        self.vm: str = None
        self.cpus: int = None
        self.hyperthreading: str = None
        self.deadline_run: int = None
        self.deadline_period: int = None
        self.deadline_period_factor: float = None
        self.hpet: str = None
        self.tsc: str = None
        self.chaos: str = None
        self.loadperc: int = None
        self.qdisc: str = None
        self.vms: int = None
        self.pacing: str = None
        self.os: str = None
        self.socket_buffer: str = None
        self.socketbuf: str = None
    
    def fill_from_dict(self, dict):
        for key in dict:
            if dict[key] is None:
                continue
            if key in self.__dict__:
                if type(dict[key]) is list:
                    self.__dict__[key] = dict[key]
                else:
                    self.__dict__[key] = [dict[key]]
    
    def apply(self, meta) -> bool:
        for filter_option in self.__dict__:
            if filter_option == "timestamp":
                continue
            if self.__dict__[filter_option] is None:
                continue
            if filter_option == "buffer_size_bytes":
                metaval = int(float(meta[filter_option]))
            elif filter_option == "loss_mode":
                metaval = meta["loss"]["mode"]
            else:
                if not filter_option in meta:
                    return False
                metaval = meta[filter_option]
            required_vals = self.__dict__[filter_option]
            fit = False
            for required_val in required_vals:
                if filter_option == "default_qdisc":
                    if required_val == "default":
                        metaval = metaval.split(":")[0]
                    else:
                        metaval = metaval.split(":")[-1]
                if type(required_val) == str and "\\t" in required_val:
                    required_val = required_val.replace("\\t", "")
                if  type(metaval) == str and "\\t" in metaval:
                    metaval = metaval.replace("\\t", "")
                if type(required_val) == str and required_val.startswith("_"):
                    notflag = True
                    required_val = required_val.replace("_", "")
                else:
                    notflag = False

                if notflag != (required_val == metaval):
                    fit = True
                    break
            if not fit:
                return False            
        return True



def buffer_bytes_to_bdp(row):
    buffer_bytes = int(row["buffer_size_bytes"])
    rate_mbit = int(row["rate"])
    rtt_ms = int(row["delay_rtt"])

    rate_bit_s = float(rate_mbit * 1000000)
    rate_byte_s = rate_bit_s / 8
    rtt_s = float(rtt_ms / 1000)
    return (buffer_bytes/rate_byte_s)/rtt_s


def throughput_relative(row) -> float:
    avg_throughput_bps = row["bits_per_second"]
    max_bandwidth = int(row["rate"])
    if avg_throughput_bps/1000000 > max_bandwidth:# or avg_throughput_bps/1000000 < 0:
        return None
    return float((avg_throughput_bps/1000000)/max_bandwidth)


def preprocess_meta(meta):
    meta["bdp"] = round(buffer_bytes_to_bdp(meta), 4)
    meta["kernel"] = meta["kernel"].replace('BBRv3', 'zkernel6-13-BBRv3')
    meta["kernel"] = meta["kernel"].replace('BBRv2', 'zkernel5-13-BBRv2')
    meta["kernel"] = meta["kernel"].replace('_fixed', '-patched')
    meta["bandwidth_delay_product"] = (float(meta["delay_rtt"])/1000) * float(meta["rate"])
    meta["loss_mode"] = meta["loss"]["mode"]
    meta["n"] = int(meta["n"])

    if not "vms" in meta:
        meta["vms"] = 0
    meta["vms"] = int(meta["vms"])

    if not "pacing" in meta:
        meta["pacing"] = ""
    if "contention" in meta:
        del meta["contention"]

    meta['delay_rtt'] = float(meta['delay_rtt'])
    meta['rate'] = float(meta['rate'])
    meta['bdp'] = float(meta['bdp'])
    if "cpus" in meta:
        meta['cpus'] = float(meta['cpus'])
    if "loadperc" in meta:
        meta['loadperc'] = int(meta['loadperc'])
    try:
        meta['parallel'] = float(meta['parallel'])
    except:
        pass

    if "hyperthreading" in meta:
        meta["hyperthreading"] = True if meta["hyperthreading"] == "on" else False
    else:
        meta["hyperthreading"] = True

    if not "tso" in meta:
        meta["tso"] = "on"

    if not "os" in meta:
        if meta["vm"] == "virtualbox":
            meta["os"] = "debian"
        elif meta["vm"] == "qemu_kvm" or meta["vm"] == "qemu":
            meta["os"] = "busybox"

    if not "qdisc" in meta:
        meta["qdisc"] = ""

    if not "setup" in meta:
        meta["setup"] = "old"
    
    if not "hpet" in meta:
        meta["hpet"] = "off"
    
    if not "tsc" in meta:
        meta["tsc"] = "default"
    
    if not "hostq" in meta:
        meta["hostq"] = "default"
    
    if not "chaos" in meta:
        meta["chaos"] = "none"
    
    if not "loadperc" in meta:
        meta["loadperc"] = "none"
    
    if not "deadline_run" in meta or not "deadline_period" in meta:
        meta["deadline_run"] = None
        meta["deadline_period"] = None
    else:
        meta["deadline_run"] = int(meta["deadline_run"])
        meta["deadline_period"] = int(meta["deadline_period"])
        try:
            meta["deadline_period_factor"] = meta["deadline_period"]/meta["deadline_run"]
        except: 
            meta["deadline_period_factor"] = 0


    if not "cpus" in meta:
        if meta["vm"] == "virtualbox" and meta["kernel"] != "kernel5-10":
            meta["cpus"] = 4
        else:
            meta["cpus"] = 1

    if meta["loss_mode"] != "random":
        meta["random_loss_rate"] = 0.0
    else:
        meta["random_loss_rate"] = float(meta["loss"]["params"])
    if meta["loss_mode"] != "gemodel":
        meta["gemodel_q"] = 0
    else:
        meta["gemodel_q"] = meta["loss"]["params"].split(" ")[1]
    if not "cca" in meta:
        if "BBR" in meta["kernel"]:
            meta["original_cca"]="bbr"
            meta["cca"] = "bbr"
        else:
            meta["original_cca"]="cubic"
            meta["cca"] = "cubic"
    else:
        meta["original_cca"]=meta["cca"]
        if meta["cca"] == "bbr" and (meta["kernel"] == "zkernel6-13-BBRv3"):
            meta["cca"] = "bbr3"
            meta["test_cca"] = "yes"
        elif meta["cca"] == "bbr" and (meta["kernel"] == "kernel6-1"):
            meta["cca"] = "bbr"
            meta["test_cca"] = "yes"
        elif meta["cca"] == "cubic" and (meta["kernel"] == "kernel6-1"):
            meta["cca"] = "cubic"
            meta["test_cca"] = "yes"
        elif meta["cca"] == "bbr" and meta["kernel"] == "zkernel6-13-BBRv3-patched":
            meta["cca"] = "bbr3-patched"
            meta["test_cca"] = "yes"
        elif meta["cca"] == "bbr1" and meta["kernel"] == "zkernel6-13-BBRv3":
            meta["cca"] = "bbr"
        elif meta["cca"] == "bbr1" and  meta["kernel"] == "zkernel6-13-BBRv3-patched":
            meta["cca"] = "bbr-patchedv3"
        elif meta["cca"] == "bbr" and  meta["kernel"] == "kernel6-1-patched":
            meta["cca"] = "bbr-patched"
            meta["test_cca"] = "yes"
        elif meta["cca"] == "bbr" and  meta["kernel"] == "kernel6-1-patched_new_new":
            meta["cca"] = "bbr-patched-new-new"
            meta["test_cca"] = "yes"
        elif meta["cca"] == "bbr" and  meta["kernel"] == "zkernel6-13-BBRv3-patched_new":
            meta["cca"] = "bbr3-patched-new"
            meta["test_cca"] = "yes"
        elif meta["cca"] == "bbr" and  meta["kernel"] == "zkernel6-13-BBRv3-patched_new_new":
            meta["cca"] = "bbr3-patched-new-new"
            meta["test_cca"] = "yes"
        elif meta["cca"] == "bbr2" and meta["kernel"] == "zkernel5-13-BBRv2":
            meta["cca"] = "bbr2"
            meta["test_cca"] = "yes"
        elif meta["cca"] == "bbr" and meta["kernel"] == "zkernel5-13-BBRv2":
            meta["cca"] = "bbr"
        elif meta["cca"] == "bbr2" and meta["kernel"] == "zkernel5-13-BBRv2-patched":
            meta["cca"] = "bbr2-patched"
            meta["test_cca"] = "yes"
    if not "test_cca" in meta:
        meta["test_cca"] = "no"
    if not "sysctl_cmd" in meta or not "default_qdisc" in meta["sysctl_cmd"]:
        if meta["kernel"] == "kernel6-1":
            meta["default_qdisc"] = "default:fq_codel"
        else:
            meta["default_qdisc"] = "default:pfifo_fast"
    else:
        meta["default_qdisc"] = meta["sysctl_cmd"].split("=")[1]
    
    if "socketbuf" in meta:
        del meta["socketbuf"]
    return meta


def get_report(sender_path, meta, logdir, avg_results):
    reports = []
    for iperf_report in sorted(os.listdir(sender_path)):
        if not iperf_report.startswith("iperf"):
            continue
        reports.append(os.path.join(sender_path, iperf_report))
    
    if len(reports) != int(meta["n"]):
        print("Not the expected length", len(reports), int(meta["n"]), logdir)

    for i, sender_iperf_log in enumerate(reports):
        if sender_iperf_log.endswith(".json"):
            with open(sender_iperf_log, "r") as json_log:
                try:
                    tmp_res = json.load(json_log)
                except:
                    break
                if tmp_res is None:
                    print("-",logdir)
                    break
                    continue
                if "error" in tmp_res:
                    print(logdir, tmp_res["error"])
                    break
                    continue
                if not (meta["original_cca"] == tmp_res["end"]["sender_tcp_congestion"] and meta["parallel"] == tmp_res["start"]["test_start"]["num_streams"]):
                    print("wrong classification?", logdir)
                    break
                avg_results['start'].append(float(tmp_res["end"]["sum_received"]["start"]))
                avg_results['end'].append(float(tmp_res["end"]["sum_received"]["end"]))
                avg_results['bytes'].append(float(tmp_res["end"]["sum_received"]["bytes"]))
                avg_results['bits_per_second'].append(float(tmp_res["end"]["sum_received"]["bits_per_second"]))
                avg_results['mbps_timeseries'].append([float(x["sum"]["bits_per_second"])/1000000 for x in tmp_res["intervals"]])
                avg_results['rttms_timeseries'].append([float(x["streams"][0]["rtt"])/1000.0 for x in tmp_res["intervals"]])
                avg_results['retransmits'].append(float(tmp_res["end"]["sum_sent"]["retransmits"]))
                avg_results['cpu_host_total'].append(float(tmp_res["end"]["cpu_utilization_percent"]["host_total"]))
                avg_results['cpu_remote_total'].append(float(tmp_res["end"]["cpu_utilization_percent"]["remote_total"]))
                avg_results['cpu_host_user'].append(float(tmp_res["end"]["cpu_utilization_percent"]["host_user"]))
                avg_results['cpu_host_system'].append(float(tmp_res["end"]["cpu_utilization_percent"]["host_system"]))
        
        else:
            continue

        avg_results["timestamp"].append(logdir)
        avg_results["iteration"].append(i)

        if not "adapter_type" in meta:
            print("adater_type", logdir)
        for m in meta:
            if m == "download_bytes":
                continue
            if m == "duration_sec":
                continue
            if m == "loss_rate_uniform":
                continue
            if m == "adapter_type":
                continue
            if m in avg_results:
                avg_results[m].append(str(meta[m]))
            else:
                avg_results[m] = [str(meta[m])]
    
    return avg_results


def logs_to_df(base_path: str, filter: Filter):
    avg_results = {
        "start": [],
        "end": [],
        "bytes": [],
        "bits_per_second": [],
        "mbps_timeseries": [],
        "rttms_timeseries": [],
        "retransmits": [],
        "timestamp": [],
        "iteration": [],
        "cpu_host_total": [],
        "cpu_host_user": [],
        "cpu_host_system": [],
        "cpu_remote_total" : [],
    }

    for logdir in sorted(os.listdir(base_path)):
        logdir_clean = logdir
        if not logdir_clean.startswith("202"):
            continue
        if filter.timestamp and not (logdir_clean.startswith(filter.timestamp[0]) or logdir_clean.startswith(filter.timestamp[1]) or logdir_clean.startswith(filter.timestamp[2]) or logdir_clean.startswith(filter.timestamp[3])):
            continue

        logdir_path = os.path.join(base_path, logdir)
        meta_file = os.path.join(logdir_path, "meta.json")
        try:
            with open(meta_file) as j: 
                meta = json.load(j)
        except:
            print("error json load", meta_file)
            continue
        
        meta = preprocess_meta(meta)
        
        sender_path = os.path.join(logdir_path, "sender")
        for iperf_report in sorted(os.listdir(sender_path)):
            if not iperf_report.startswith("iperf"):
                continue
            if iperf_report.endswith(".json"):
                meta["json"] = True
                break
            elif iperf_report.endswith(".log"):
                meta["json"] = False
                break

        if not filter.apply(meta):
            continue

        avg_results = get_report(sender_path, meta, logdir, avg_results)


    for av in avg_results:
        print(av, len(avg_results[av]))
    df = pd.DataFrame(avg_results)
    if df.empty:
        print("No data.")
        return None
    df['delay_rtt'] = df['delay_rtt'].astype(float)
    df['random_loss_rate'] = df['random_loss_rate'].astype(float)
    df['rate'] = df['rate'].astype(float)
    df['rate'] = df['rate'].astype(int)
    df['bdp'] = df['bdp'].astype(float)#
    df['bandwidth_delay_product'] = df['bandwidth_delay_product'].astype(float)
    df['bdp'] = df['bdp'].round(4)
    df['parallel'] = df['parallel'].astype(float)
    df['cpus'] = df['cpus'].astype(float)
    try:
        df['loadperc'] = df['loadperc'].astype(int)
    except:
        pass
    try:
        df["deadline_run"] = df['deadline_run'].astype(int)
        df["deadline_period"] = df['deadline_period'].astype(int)
        df["deadline_period_factor"] = df['deadline_period_factor'].astype(float)
    except:
        pass
    try:
        df["vms"] = df["vms"].astype(int)
    except:
        pass
    df = df.drop('buffer_size_bytes', axis=1)
    df["utilization_mbits_per_second"] = df.apply(throughput_relative, axis=1)

    return df

