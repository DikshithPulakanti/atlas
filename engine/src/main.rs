use tracing::info;
use tracing_subscriber;

mod compiler;
mod executor;
mod server;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();
    info!("Atlas Engine starting...");
}
