<template>
  <div class="border rounded-lg min-h-[200px]">
    <div v-if="editor" class="p-2 bg-gray-100 dark:bg-gray-800 border-b flex flex-wrap items-center gap-2">
      <button type="button" @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }" class="btn-editor">H1</button>
      <button type="button" @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }" class="btn-editor">H2</button>
      <button type="button" @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }" class="btn-editor">H3</button>
      <button type="button" @click="editor.chain().focus().setParagraph().run()" :class="{ 'is-active': editor.isActive('paragraph') }" class="btn-editor">P</button>
      <button type="button" @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }" class="btn-editor">Bold</button>
      <button type="button" @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }" class="btn-editor">Italic</button>
      <button type="button" @click="editor.chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }" class="btn-editor">Strike</button>
      <button type="button" @click="editor.chain().focus().toggleBulletList().run()" :class="{ 'is-active': editor.isActive('bulletList') }" class="btn-editor">項目符號</button>
      <button type="button" @click="editor.chain().focus().toggleOrderedList().run()" :class="{ 'is-active': editor.isActive('orderedList') }" class="btn-editor">編號清單</button>
      <button type="button" @click="editor.chain().focus().setHorizontalRule().run()" class="btn-editor">分隔線</button>
      <button type="button" @click="addImage" class="btn-editor">圖片</button>
      <select @change="changeFontSize($event)" class="btn-editor bg-white dark:bg-gray-700 dark:text-white">
        <option value="">預設字體</option>
        <option value="12px">12px</option>
        <option value="14px">14px</option>
        <option value="16px">16px</option>
        <option value="18px">18px</option>
        <option value="20px">20px</option>
        <option value="24px">24px</option>
      </select>
    </div>
    <editor-content :editor="editor" />
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import Image from "@tiptap/extension-image";
import apiClient from '../api/axios';
import TextStyle from '@tiptap/extension-text-style';
import { Extension } from '@tiptap/core';
import { watch } from 'vue';

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    fontSize: {
      setFontSize: (size: string) => ReturnType;
      unsetFontSize: () => ReturnType;
    }
  }
}

// Custom FontSize extension
const FontSize = Extension.create({
  name: 'fontSize',
  addOptions() {
    return {
      types: ['textStyle'],
    };
  },
  addGlobalAttributes() {
    return [
      {
        types: this.options.types,
        attributes: {
          fontSize: {
            default: null,
            parseHTML: element => element.style.fontSize.replace(/px$/, ''),
            renderHTML: attributes => {
              if (!attributes.fontSize) {
                return {};
              }
              return { style: `font-size: ${attributes.fontSize}px` };
            },
          },
        },
      },
    ];
  },
  addCommands() {
    return {
      setFontSize: (fontSize) => ({ chain }) => {
        return chain().setMark('textStyle', { fontSize: fontSize }).run();
      },
      unsetFontSize: () => ({ chain }) => {
        return chain().setMark('textStyle', { fontSize: null }).removeEmptyTextStyle().run();
      },
    };
  },
});

const props = defineProps({ modelValue: String });
const emit = defineEmits(['update:modelValue']);

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Image,
    TextStyle,
    FontSize,
  ],
  editorProps: {
    attributes: {
      class: 'prose dark:prose-invert max-w-none p-4 focus:outline-none min-h-[200px]',
    },
  },
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML());
  },
});

watch(() => props.modelValue, (newValue) => {
  if (editor.value && editor.value.getHTML() !== newValue) {
    editor.value.commands.setContent(newValue || '', false);
  }
});

const addImage = async () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  input.onchange = async () => {
    if (input.files) {
      const file = input.files[0];
      const formData = new FormData();
      formData.append('image', file);
      try {
        const response = await apiClient.post('/images/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        if (response.data.url) {
          editor.value?.chain().focus().setImage({ src: response.data.url }).run();
        }
      } catch (error) {
        console.error('Image upload failed', error);
        alert('圖片上傳失敗');
      }
    }
  };
  input.click();
};

const changeFontSize = (event: Event) => {
  const target = event.target as HTMLSelectElement;
  const fontSize = target.value;
  if (fontSize) {
    editor.value?.chain().focus().setFontSize(fontSize).run();
  } else {
    editor.value?.chain().focus().unsetFontSize().run();
  }
};

</script>

<style>
.btn-editor {
  @apply px-3 py-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-sm;
}
.is-active {
  @apply bg-gray-300 dark:bg-gray-600;
}
</style>
