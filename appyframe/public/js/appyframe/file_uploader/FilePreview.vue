<template>
	<div class="file-preview">
		<div class="file-icon">
			<img v-if="is_image" :src="src" :alt="file.name" />
			<div class="fallback" v-else v-html="appyframe.utils.icon('file', 'md')"></div>
		</div>
		<div>
			<div>
				<a class="flex" :href="file.doc.file_url" v-if="file.doc" target="_blank">
					<span class="file-name">{{ file.name }}</span>
				</a>
				<span class="file-name" v-else>{{ file.name }}</span>
			</div>

			<div>
				<span class="file-size">
					{{ file_size }}
				</span>
			</div>

			<div class="flex config-area">
				<label v-if="is_optimizable" class="appyframe-checkbox"
					><input
						type="checkbox"
						:checked="optimize"
						@change="emit('toggle_optimize')"
					/>{{ __("Optimize") }}</label
				>
				<label class="appyframe-checkbox"
					><input
						type="checkbox"
						:checked="file.private"
						@change="emit('toggle_private')"
					/>{{ __("Private") }}</label
				>
			</div>
			<div>
				<span v-if="file.error_message" class="file-error text-danger">
					{{ file.error_message }}
				</span>
			</div>
		</div>
		<div class="file-actions">
			<ProgressRing
				v-show="file.uploading && !uploaded && !file.failed"
				primary="var(--primary-color)"
				secondary="var(--gray-200)"
				:radius="24"
				:progress="progress"
				:stroke="3"
			/>
			<div v-if="uploaded" v-html="appyframe.utils.icon('solid-success', 'lg')"></div>
			<div v-if="file.failed" v-html="appyframe.utils.icon('solid-error', 'lg')"></div>
			<div class="file-action-buttons">
				<button
					v-if="is_cropable"
					class="btn btn-crop muted"
					@click="emit('toggle_image_cropper')"
					v-html="appyframe.utils.icon('crop', 'md')"
				></button>
				<button
					v-if="!uploaded && !file.uploading && !file.failed"
					class="btn muted"
					@click="emit('remove')"
					v-html="appyframe.utils.icon('delete', 'md')"
				></button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import ProgressRing from "./ProgressRing.vue";

// emits
let emit = defineEmits(["toggle_optimize", "toggle_private", "toggle_image_cropper", "remove"]);

// props
const props = defineProps({
	file: Object,
});

// variables
let src = ref(null);
let optimize = ref(props.file.optimize);

// computed
let file_size = computed(() => {
	return appyframe.form.formatters.FileSize(props.file.file_obj.size);
});
let is_private = computed(() => {
	return props.file.doc ? props.file.doc.is_private : props.file.private;
});
let uploaded = computed(() => {
	return props.file.request_succeeded;
});
let is_image = computed(() => {
	return props.file.file_obj.type.startsWith("image");
});
let is_optimizable = computed(() => {
	let is_svg = props.file.file_obj.type == "image/svg+xml";
	return is_image.value && !is_svg && !uploaded.value && !props.file.failed;
});
let is_cropable = computed(() => {
	let croppable_types = ["image/jpeg", "image/png"];
	return (
		!uploaded.value &&
		!props.file.uploading &&
		!props.file.failed &&
		croppable_types.includes(props.file.file_obj.type)
	);
});
let progress = computed(() => {
	let value = Math.round((props.file.progress * 100) / props.file.total);
	if (isNaN(value)) {
		value = 0;
	}
	return value;
});

// mounted
onMounted(() => {
	if (is_image.value) {
		if (window.FileReader) {
			let fr = new FileReader();
			fr.onload = () => (src.value = fr.result);
			fr.readAsDataURL(props.file.file_obj);
		}
	}
});
</script>

<style scoped>
.file-preview {
	display: flex;
	align-items: center;
	padding: 0.75rem;
	border: 1px solid transparent;
}

.file-preview + .file-preview {
	border-top-color: var(--border-color);
}

.file-preview:hover {
	background-color: var(--bg-color);
	border-color: var(--dark-border-color);
	border-radius: var(--border-radius);
}

.file-preview:hover + .file-preview {
	border-top-color: transparent;
}

.file-icon {
	border-radius: var(--border-radius);
	width: 2.625rem;
	height: 2.625rem;
	overflow: hidden;
	margin-right: var(--margin-md);
	flex-shrink: 0;
}

.file-icon img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.file-icon .fallback {
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
	border: 1px solid var(--border-color);
	border-radius: var(--border-radius);
}

.file-name {
	font-size: var(--text-base);
	font-weight: var(--text-bold);
	color: var(--text-color);
	display: -webkit-box;
	-webkit-line-clamp: 1;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.file-size {
	font-size: var(--text-sm);
	color: var(--text-light);
}

.file-actions {
	width: 3rem;
	flex-shrink: 0;
	margin-left: auto;
	text-align: center;
}

.file-actions .btn {
	padding: var(--padding-xs);
	box-shadow: none;
}

.file-action-buttons {
	display: flex;
	justify-content: flex-end;
}

.muted {
	opacity: 0.5;
	transition: 0.3s;
}

.muted:hover {
	opacity: 1;
}

.appyframe-checkbox {
	font-size: var(--text-sm);
	color: var(--text-light);
	display: flex;
	align-items: center;
	padding-top: 0.25rem;
}

.config-area {
	gap: 0.5rem;
}

.file-error {
	font-size: var(--text-sm);
	font-weight: var(--text-bold);
}
</style>
