use std::net::SocketAddr;

use tonic::transport::Server;
use tracing::info;
use tracing_subscriber::EnvFilter;

use atlas_engine::proto::atlas_engine_service_server::AtlasEngineServiceServer;
use atlas_engine::server::grpc::AtlasGrpcService;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()))
        .init();

    let addr: SocketAddr = "0.0.0.0:50061".parse()?;
    let service = AtlasGrpcService::default();

    info!("Atlas Engine listening on {addr}");

    Server::builder()
        .add_service(AtlasEngineServiceServer::new(service))
        .serve(addr)
        .await?;

    Ok(())
}
