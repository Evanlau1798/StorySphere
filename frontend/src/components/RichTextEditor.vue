<template>
  <div class="border rounded-lg min-h-[300px] flex flex-col bg-white dark:bg-gray-800 shadow-sm">
    <div v-if="editor" class="p-2 border-b flex flex-wrap items-center gap-1 bg-gray-50 dark:bg-gray-900 sticky top-0 z-10 rounded-t-lg">
      
      <!-- Headings -->
      <div class="flex items-center gap-1 pr-2 border-r border-gray-300 dark:border-gray-700">
        <button type="button" @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }" class="btn-editor" title="大標題">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16"/><path d="M4 6v12"/><path d="M12 6v12"/><path d="M20 6v12"/></svg>
        </button>
        <button type="button" @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }" class="btn-editor" title="中標題">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16"/><path d="M4 6v12"/><path d="M20 6v12"/></svg>
        </button>
        <button type="button" @click="editor.chain().focus().setParagraph().run()" :class="{ 'is-active': editor.isActive('paragraph') }" class="btn-editor" title="段落">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 4v16"/><path d="M17 4v16"/><path d="M19 4H9.5a4.5 4.5 0 0 0 0 9H13"/></svg>
        </button>
      </div>

      <!-- Formatting -->
      <div class="flex items-center gap-1 px-2 border-r border-gray-300 dark:border-gray-700">
        <button type="button" @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }" class="btn-editor" title="粗體">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/><path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/></svg>
        </button>
        <button type="button" @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }" class="btn-editor" title="斜體">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg>
        </button>
        <button type="button" @click="editor.chain().focus().toggleUnderline().run()" :class="{ 'is-active': editor.isActive('underline') }" class="btn-editor" title="底線">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v7a6 6 0 0 0 6 6 6 6 0 0 0 6-6V3"/><line x1="4" y1="21" x2="20" y2="21"/></svg>
        </button>
        <button type="button" @click="editor.chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }" class="btn-editor" title="刪除線">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
        </button>
        <button type="button" @click="editor.chain().focus().toggleHighlight().run()" :class="{ 'is-active': editor.isActive('highlight') }" class="btn-editor" title="螢光筆">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 11-6 6v3h9l3-3"/><path d="m22 7-3-3"/><path d="m18 3-3.9 3.9"/></svg>
        </button>
      </div>

      <!-- Alignment -->
      <div class="flex items-center gap-1 px-2 border-r border-gray-300 dark:border-gray-700">
        <button type="button" @click="editor.chain().focus().setTextAlign('left').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) }" class="btn-editor" title="靠左對齊">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="17" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="3" y2="18"/></svg>
        </button>
        <button type="button" @click="editor.chain().focus().setTextAlign('center').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }" class="btn-editor" title="置中對齊">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="21" y1="10" x2="3" y2="10"/><line x1="17" y1="6" x2="7" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="7" y2="18"/></svg>
        </button>
        <button type="button" @click="editor.chain().focus().setTextAlign('right').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }" class="btn-editor" title="靠右對齊">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="21" y1="10" x2="7" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="21" y1="18" x2="7" y2="18"/></svg>
        </button>
      </div>

       <!-- Lists -->
      <div class="flex items-center gap-1 px-2 border-r border-gray-300 dark:border-gray-700">
        <button type="button" @click="editor.chain().focus().toggleBulletList().run()" :class="{ 'is-active': editor.isActive('bulletList') }" class="btn-editor" title="項目符號">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
        </button>
        <button type="button" @click="editor.chain().focus().toggleOrderedList().run()" :class="{ 'is-active': editor.isActive('orderedList') }" class="btn-editor" title="編號清單">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="10" y1="6" x2="21" y2="6"/><line x1="10" y1="12" x2="21" y2="12"/><line x1="10" y1="18" x2="21" y2="18"/><path d="M4 6h1v4"/><path d="M4 10h2"/><path d="M6 18H4c0-1 2-2 2-3s-1-1.5-2-1"/></svg>
        </button>
      </div>

      <!-- Logic -->
      <div class="flex items-center gap-1 pl-2">
        <button type="button" @click="editor.chain().focus().setHorizontalRule().run()" class="btn-editor" title="分隔線">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </button>
        <button type="button" @click="addImage" class="btn-editor" title="插入圖片">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
        </button>
        <select @change="changeFontSize($event)" class="ml-2 px-2 py-1 rounded text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white border-0 cursor-pointer focus:ring-1">
          <option value="">字體</option>
          <option value="12px">12px</option>
          <option value="14px">14px</option>
          <option value="16px">16px</option>
          <option value="18px">18px</option>
          <option value="20px">20px</option>
          <option value="24px">24px</option>
        </select>
      </div>
    </div>
    
    <div class="flex-grow bg-white dark:bg-gray-800 rounded-b-lg">
      <editor-content :editor="editor" class="min-h-[300px]" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import Image from "@tiptap/extension-image";
import apiClient from '../api/axios';
import { TextStyle } from '@tiptap/extension-text-style';
import { Extension } from '@tiptap/core';
import { watch } from 'vue';

// New Extensions
import Placeholder from '@tiptap/extension-placeholder';
import TextAlign from '@tiptap/extension-text-align';
import Underline from '@tiptap/extension-underline';
import Highlight from '@tiptap/extension-highlight';

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
              return { style: `font-size: ${attributes.fontSize}` };
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
        return chain().unsetMark('textStyle').run();
      },
    };
  },
});

const props = defineProps({ modelValue: String, placeholder: String });
const emit = defineEmits(['update:modelValue']);

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Image,
    TextStyle,
    FontSize as any,
    Underline,
    Highlight,
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
    Placeholder.configure({
      placeholder: props.placeholder || '請在此輸入內容...',
    }),
  ],
  editorProps: {
    attributes: {
      class: 'prose dark:prose-invert max-w-none p-4 focus:outline-none min-h-[300px]',
    },
  },
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML());
  },
});

watch(() => props.modelValue, (newValue) => {
  if (editor.value && editor.value.getHTML() !== newValue) {
    // Tiptap 2.x/3.x: setContent(content, emitUpdate) -> boolean or options object in newer versions?
    // Based on error: "Type 'false' has no properties in common with type 'SetContentOptions'."
    // So it expects an object.
    editor.value.commands.setContent(newValue || '', { emitUpdate: false });
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
  
  // Reset value to allow selecting same file again
  input.value = '';
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

<style scoped>
.btn-editor {
  @apply p-1.5 rounded hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors;
}
.is-active {
  @apply bg-blue-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400;
}
/* Ensure default text color for editor so placeholder shows correctly */
.ProseMirror p.is-editor-empty:first-child::before {
  color: #adb5bd;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}
</style>
