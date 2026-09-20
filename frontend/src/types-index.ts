export interface NodeStatus {
  connected: boolean;
  chain?: string;
  block_height?: number;
  headers?: number;
  verification_progress?: number;
  is_synced: boolean;
  peer_count?: number;
  difficulty?: number;
  network_hashrate?: number;
  uptime_seconds?: number;
  version?: string;
  error?: string;
}

export interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  memory_used_mb: number;
  memory_total_mb: number;
  disk_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  temperature_celsius: number | null;
  host_uptime_seconds: number;
}

export interface Miner {
  worker_name: string;
  ip_address: string | null;
  hashrate: number;
  accepted_shares: number;
  rejected_shares: number;
  last_share_at: string | null;
  connected_since: string | null;
  uptime_seconds: number | null;
  is_online: boolean;
}

export interface HashratePoint {
  timestamp: string;
  hashrate: number;
}

export interface Transaction {
  txid: string;
  category: string;
  amount: number;
  confirmations: number;
  time: string;
  is_mining_reward: boolean;
}

export interface WalletInfo {
  address: string | null;
  balance: number;
  unconfirmed_balance: number;
  transactions: Transaction[];
  last_mining_rewards: Transaction[];
}

export interface EventItem {
  id: number;
  timestamp: string;
  category: string;
  severity: "info" | "warning" | "error" | "critical";
  message: string;
}

export interface UserOut {
  id: string;
  username: string;
  role: "admin" | "operator" | "viewer";
  is_active: boolean;
  must_change_password: boolean;
  created_at: string;
  last_login: string | null;
}
