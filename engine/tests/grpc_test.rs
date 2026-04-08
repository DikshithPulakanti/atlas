use std::net::SocketAddr;

use atlas_engine::proto::{
    atlas_engine_service_client::AtlasEngineServiceClient,
    atlas_engine_service_server::AtlasEngineServiceServer, ValidateQueryRequest,
};
use atlas_engine::server::grpc::AtlasGrpcService;
use tokio::net::TcpListener;
use tonic::transport::{Channel, Server};

/// Spawn the gRPC server on an ephemeral port, return the address.
async fn start_server() -> SocketAddr {
    let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let addr = listener.local_addr().unwrap();

    tokio::spawn(async move {
        let incoming = tokio_stream::wrappers::TcpListenerStream::new(listener);
        Server::builder()
            .add_service(AtlasEngineServiceServer::new(AtlasGrpcService::default()))
            .serve_with_incoming(incoming)
            .await
            .unwrap();
    });

    addr
}

#[tokio::test]
async fn validate_query_returns_valid() {
    let addr = start_server().await;

    let channel = Channel::from_shared(format!("http://{addr}"))
        .unwrap()
        .connect()
        .await
        .unwrap();

    let mut client = AtlasEngineServiceClient::new(channel);

    let response = client
        .validate_query(ValidateQueryRequest {
            query: "SELECT * FROM customers".into(),
        })
        .await
        .unwrap()
        .into_inner();

    assert!(response.valid);
    assert!(response.errors.is_empty());
}
