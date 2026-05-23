
## 🔥 Self-Critic RL Stage

In this step, we will load the cold-start data for GRPO training. We reference the [ReCall](https://github.com/Agent-RL/ReCall) and [VERL](https://github.com/volcengine/verl) frameworks for RL training.

### 1. Environment Setup

First, please set up the VERL environment. After that, install our environment:

```bash
# Create conda environment
conda create -n tool_star python=3.10
conda activate tool_star

# Install requirements
cd tool_star
pip install -r requirements.txt
```

### 2. Vanilla RL Training

Our training framework is based on [verl](https://github.com/volcengine/verl) and [ReCall](https://github.com/Agent-RL/ReCall). The training scripts can be found under `scripts/train`. First, you need to complete the information in `scripts/train/run_tool_star.sh`:

```bash
export PYTHONPATH=/src/verl:$PYTHONPATH
export MKL_SERVICE_FORCE_INTEL=1
export MKL_THREADING_LAYER=GNU

bash scripts/train/train.sh \
    --train_batch_size 128 \
    --ppo_mini_batch_size 16 \
    --rollout_n 8 \
    --apply_chat True \
    --prompt_template_name re_search_template_sys \
    --actor_model_path {your_actor_model_path} \
    --project_name {your_project_name} \
    --experiment_name {your_experiment_name} \
    --nnodes 1 \
    --n_gpus_per_node 8 \
    --save_freq 10 \
    --test_freq 10 \
    --total_epochs 2 \
    --swanlab_api_key {your_swanlab_api_key} \
    --save_path {your_save_path} \
    --train_files {path_to_train_file}/grpo_mix_train_shuffle.parquet \
    --test_files {path_to_test_file}/grpo_mix_test.parquet
```

The provided training scripts default to `trainer.logger="[console, swanlab]"`. `wandb` is now optional and only used if you explicitly pass `--wandb_api_key`.

Since the rollout process involves web search calls, configure the search provider with environment variables instead of hardcoding keys in code:

```bash
cp .env.example .env
```

Then edit `.env`:

```bash
WEB_SEARCH_PROVIDER=brave
WEB_SEARCH_API_KEY=your_brave_api_key
WEB_SEARCH_ENDPOINT=https://api.search.brave.com/res/v1/web/search
BRAVE_SEARCH_COUNTRY=US
BRAVE_SEARCH_LANG=en
BRAVE_SEARCH_SAFESEARCH=moderate
```

If you use `deep_search_browser_summarize()`, also configure:

```bash
WEB_SEARCH_SUMMARIZER_API_KEY=your_summarizer_api_key
WEB_SEARCH_SUMMARIZER_BASE_URL=your_openai_compatible_base_url
WEB_SEARCH_SUMMARIZER_MODEL=your_model_name
```

The rollout web search module will automatically load `.env` and use Brave search by default.

You can then run the following script to start training:

```bash
cd ./Tool_Star_RL/scripts/train/
bash run_tool_star.sh
```

For the core code of the rollout process, please refer to `/src/verl/verl/workers/rollout/vllm_rollout/vllm_rollout.py`, and for the reward calculation part, refer to `/Tool_Star_RL/src/verl/verl/utils/reward_score`. You can modify them according to your needs.
