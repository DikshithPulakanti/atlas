use tokio_stream::wrappers::ReceiverStream;
use tonic::{Request, Response, Status};
use tracing::info;

use crate::proto::{
    atlas_engine_service_server::AtlasEngineService, ExecuteQueryRequest, ExecuteQueryResponse,
    ExplainQueryRequest, ExplainQueryResponse, ExecutionPlan, ValidateQueryRequest,
    ValidateQueryResponse,
};

/// AtlasGrpcService implements the AtlasEngineService gRPC trait.
///
/// Currently returns stub responses. Once the compiler and executor are built,
/// each handler will:
///   - ExecuteQuery:  parse → plan → execute across adapters → stream batches
///   - ExplainQuery:  parse → plan → return the plan without executing
///   - ValidateQuery: parse → semantic check → return errors/warnings
#[derive(Debug, Default)]
pub struct AtlasGrpcService;

#[tonic::async_trait]
impl AtlasEngineService for AtlasGrpcService {
    type ExecuteQueryStream = ReceiverStream<Result<ExecuteQueryResponse, Status>>;

    /// Execute an AtlasQL query and stream result batches.
    ///
    /// TODO: Wire up the compiler pipeline (lexer → parser → semantic → planner)
    /// to produce an ExecutionPlan, then pass it to the ExecutionEngine which
    /// dispatches sub-queries to source adapters via gRPC and merges results.
    async fn execute_query(
        &self,
        request: Request<ExecuteQueryRequest>,
    ) -> Result<Response<Self::ExecuteQueryStream>, Status> {
        let query = request.into_inner().query;
        info!(query = %query, "ExecuteQuery called (stub)");

        let (tx, rx) = tokio::sync::mpsc::channel(1);

        // Send a single empty batch with is_last=true
        let response = ExecuteQueryResponse {
            columns: vec![],
            row_count: 0,
            is_last: true,
            metadata: None,
        };
        tx.send(Ok(response)).await.map_err(|_| {
            Status::internal("failed to send response")
        })?;

        Ok(Response::new(ReceiverStream::new(rx)))
    }

    /// Return the execution plan for a query without running it.
    ///
    /// TODO: Run the compiler pipeline up to the planner stage and return
    /// the ExecutionPlan with cost estimates from the adapter schema cache.
    async fn explain_query(
        &self,
        request: Request<ExplainQueryRequest>,
    ) -> Result<Response<ExplainQueryResponse>, Status> {
        let query = request.into_inner().query;
        info!(query = %query, "ExplainQuery called (stub)");

        Ok(Response::new(ExplainQueryResponse {
            plan: Some(ExecutionPlan {
                nodes: vec![],
                root_node_id: String::new(),
            }),
            estimated_total_cost: 0.0,
            warnings: vec![],
        }))
    }

    /// Validate an AtlasQL query for syntax and semantic errors.
    ///
    /// TODO: Run the compiler pipeline through semantic analysis and collect
    /// all errors/warnings without generating an execution plan.
    async fn validate_query(
        &self,
        request: Request<ValidateQueryRequest>,
    ) -> Result<Response<ValidateQueryResponse>, Status> {
        let query = request.into_inner().query;
        info!(query = %query, "ValidateQuery called (stub)");

        Ok(Response::new(ValidateQueryResponse {
            valid: true,
            errors: vec![],
            warnings: vec![],
        }))
    }
}
