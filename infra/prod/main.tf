module "network_base" {
  source  = "terraform-google-modules/network/google"
  version = "~> 7.0"

  project_id   = var.project_id
  network_name = "vpc-main"

  subnets = [
    {
      subnet_name   = "subnet-public"
      subnet_ip     = "10.10.10.0/24"
      subnet_region = var.region
    },
    {
      subnet_name   = "subnet-private"
      subnet_ip     = "10.10.20.0/24"
      subnet_region = var.region
    }
  ]
} 