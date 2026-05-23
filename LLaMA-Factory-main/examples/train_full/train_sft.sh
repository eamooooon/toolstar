

# module load cuda/12.1.1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "$PROJECT_ROOT"
mkdir -p logs
LOG_FILE="logs/train_sft_$(date +%Y%m%d_%H%M%S).log"
CUDA_VISIBLE_DEVICES=0,1,2,3 llamafactory-cli train examples/train_full/qwen_sft_tool_star.yaml 2>&1 | tee "$LOG_FILE"
