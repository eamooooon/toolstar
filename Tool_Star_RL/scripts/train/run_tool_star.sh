
export PYTHONPATH=/src/verl:$PYTHONPATH
export MKL_SERVICE_FORCE_INTEL=1
export MKL_THREADING_LAYER=GNU
SWANLAB_API_KEY="${SWANLAB_API_KEY:-None}"

bash scripts/train/train.sh \
    --train_batch_size 128 \
    --ppo_mini_batch_size 16 \
    --rollout_n 8 \
    --apply_chat True \
    --prompt_template_name re_search_template_sys \
    --actor_model_path models/Qwen2.5-3B-Instruct-final_sft_edition10-52 \
    --project_name Tool-Star \
    --experiment_name Qwen2.5-3B-Instruct-first \
    --nnodes 1 \
    --n_gpus_per_node 4 \
    --save_freq 10 \
    --test_freq 10 \
    --total_epochs 2 \
    --swanlab_api_key "${SWANLAB_API_KEY}" \
    --save_path models \
    --train_files data/grpo_mix_train_shuffle.parquet \
    --test_files data/grpo_mix_test.parquet
