resource "google_container_cluster" "primary" {
  name               = "my-cluster"
  location           = "us-central1"
  initial_node_count = 2

  node_locations = [
    "us-central1-a",
    "us-central1-b"
  ]

  node_config {
    machine_type = "e2-medium"
    disk_size_gb = 20
  }

  network    = google_compute_network.vpc_network.name
  subnetwork = google_compute_subnetwork.subnet.name

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS", "APISERVER", "CONTROLLER_MANAGER", "SCHEDULER"]
  }

  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }
}