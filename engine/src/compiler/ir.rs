/// IR generator — converts planner output into the protobuf ExecutionPlan IR.
///
/// Pipeline stage 5: internal plan representation → proto ExecutionPlan.
/// Serializes the plan DAG into the wire format that the execution engine
/// and adapters consume, assigning node IDs and computing final cost estimates.
pub struct IrGenerator;
