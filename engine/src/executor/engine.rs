/// Query execution engine — walks the ExecutionPlan DAG and runs it.
///
/// Dispatches ScanNodes to source adapters via gRPC, sends AIOperatorNodes
/// to the ai-operators service, performs in-engine operations (filter, project,
/// join, aggregate, sort, limit), and streams result batches back to the caller.
pub struct ExecutionEngine;
