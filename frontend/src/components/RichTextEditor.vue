<template>
  <!-- Main Container -->
  <!-- Flexible height, auto growing -->
  <div class="relative flex flex-col min-h-[50vh] w-full bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 editor-container">
    
    <!-- MOBILE ONLY: Permanent Top Status Bar -->
    <div v-if="isMobile" class="sticky top-0 z-[60] w-full bg-white/95 dark:bg-gray-900/95 border-b border-gray-200 dark:border-gray-700 p-2 flex justify-between items-center text-xs font-medium text-gray-500 dark:text-gray-400 backdrop-blur-sm transition-all duration-300">
        <div class="flex items-center gap-3">
             <span v-if="lastSavedTimeStr" class="transition-all duration-300 ml-1">
                最後儲存時間 : {{ lastSavedTimeStr }}
             </span>
             <span v-else class="ml-1">未儲存</span>
        </div>
        
        <div class="flex items-center gap-3 mr-1">
             <!-- Page Jump Button with Border -->
             <button type="button" @click="togglePageSelector" class="flex items-center gap-1 hover:text-blue-500 transition-colors border border-gray-300 dark:border-gray-600 rounded px-2 py-0.5 bg-gray-50 dark:bg-gray-800 shadow-sm">
                  <span>{{ currentPageRel }} / {{ totalPagesRel }}</span>
             </button>
             <span class="border-l border-gray-300 dark:border-gray-600 pl-3">
                 {{ wordCount }} 字
             </span>
        </div>
        
        <!-- Mobile Page Jump Popover -->
         <div v-if="showPageSelector" class="absolute top-10 right-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden z-[70]">
               <div class="max-h-48 overflow-y-auto p-2">
                   <div class="text-xs text-gray-500 mb-2 px-1 text-center">跳轉至頁面</div>
                   <div class="grid grid-cols-4 gap-2">
                       <button v-for="n in totalPagesRel" :key="n" @click="scrollToPage(n)" 
                           class="p-1 text-xs rounded hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors"
                           :class="{ 'bg-blue-500 text-white': n === currentPageRel }">
                           {{ n }}
                       </button>
                   </div>
               </div>
          </div>
          <!-- Backdrop for popover -->
          <div v-if="showPageSelector" class="fixed inset-0 z-[65]" @click="showPageSelector = false"></div>
    </div>

    <!-- Toolbar: Unified Top Board (Desktop) OR Bottom Fixed (Mobile) -->
    <div v-if="editor" 
         ref="toolbarRef"
         :style="isMobile ? null : {}" 
         :class="[
           'transition-all duration-100 ease-out flex items-center z-50 h-11',
           /* Mobile Position: fixed bottom-0 left-0 right-0 */
           isMobile ? 'fixed bottom-0 left-0 right-0 shadow-[0_-4px_10px_-1px_rgba(0,0,0,0.1)] px-1' : 'sticky top-0 rounded-t-lg border-b border-gray-200 dark:border-gray-700 justify-between px-4',
           isMobile && !isToolbarVisible ? 'translate-y-full' : 'translate-y-0',
           'bg-white/95 dark:bg-gray-900/95 backdrop-blur-md'
         ]"
    >
      
      <!-- Toolbar Buttons -->
      <!-- On Mobile: Use w-full and justify-evenly / flex-1 for groups to fill space -->
      <div class="flex items-center gap-1 overflow-x-auto no-scrollbar" :class="isMobile ? 'w-full justify-evenly' : ''">
      
          <!-- Group 1: Styles -->
          <div class="flex items-center gap-1 shrink-0" :class="isMobile ? 'flex-1 justify-center' : ''">
            <button type="button" @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }" class="btn-editor" title="粗體">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/><path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/></svg>
            </button>
            <button type="button" @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }" class="btn-editor" title="斜體">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg>
            </button>
            <button type="button" @click="editor.chain().focus().toggleStrike().run()" :class="{ 'is-active': editor.isActive('strike') }" class="btn-editor" title="刪除線">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.3 19c-1.4 1.2-3.2 2-5.3 2a8 8 0 0 1 0-16c2.1 0 3.9.8 5.3 2"/><line x1="4" y1="12" x2="20" y2="12"/></svg>
            </button>
          </div>
          
           <!-- Divider -->
          <div class="w-px h-5 bg-gray-300 dark:bg-gray-600 shrink-0"></div>

           <!-- Group 2: Font Size -->
           <div :class="isMobile ? 'flex-1 flex justify-center' : ''">
               <button type="button" @click="cycleFontSize" class="btn-editor font-serif font-bold text-sm shrink-0 w-8" title="字體大小">
                  {{ currentFontSizeLabel }}
               </button>
           </div>
           
           <!-- Divider -->
          <div class="w-px h-5 bg-gray-300 dark:bg-gray-600 shrink-0"></div>

          <!-- Group 3: Alignment -->
          <div class="flex items-center gap-0.5 shrink-0" :class="isMobile ? 'flex-1 justify-center' : ''">
              <button type="button" @click="editor.chain().focus().setTextAlign('left').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'left' }) || (!editor.isActive({ textAlign: 'center' }) && !editor.isActive({ textAlign: 'right' })) }" class="btn-editor" title="靠左">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="17" y1="10" x2="3" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="3" y2="18"/></svg>
              </button>
               <button type="button" @click="editor.chain().focus().setTextAlign('center').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'center' }) }" class="btn-editor" title="置中">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="21" y1="10" x2="3" y2="10"/><line x1="17" y1="6" x2="7" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="17" y1="18" x2="7" y2="18"/></svg>
              </button>
               <button type="button" @click="editor.chain().focus().setTextAlign('right').run()" :class="{ 'is-active': editor.isActive({ textAlign: 'right' }) }" class="btn-editor" title="靠右">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="21" y1="10" x2="7" y2="10"/><line x1="21" y1="6" x2="3" y2="6"/><line x1="21" y1="14" x2="3" y2="14"/><line x1="21" y1="18" x2="7" y2="18"/></svg>
              </button>
          </div>
          
           <!-- Divider -->
          <div class="w-px h-5 bg-gray-300 dark:bg-gray-600 shrink-0"></div>

          <!-- Group 4: Utils -->
          <div class="flex items-center gap-1 shrink-0" :class="isMobile ? 'flex-1 justify-center' : ''">
            <button type="button" @click="editor.chain().focus().setHorizontalRule().run()" class="btn-editor" title="分隔線">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>
            </button>
            <button type="button" @click="insertPageBreak" class="btn-editor" title="插入換頁">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-2.5Z"/><path d="M12 2v20"/><path d="M8 12h8" stroke-dasharray="2 2"/></svg>
            </button>
             <button type="button" @click="addImage" class="btn-editor" title="插入圖片">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            </button>
          </div>
      </div>
      
      <!-- DESKTOP STATUS INFO -->
      <div v-if="!isMobile" class="flex items-center gap-4 border-l border-gray-300 dark:border-gray-600 pl-4 ml-2 shrink-0 text-xs font-medium text-gray-500 dark:text-gray-400">
         <span v-if="lastSavedTimeStr" class="whitespace-nowrap">最後儲存時間 : {{ lastSavedTimeStr }}</span>
         <span v-else class="whitespace-nowrap">未儲存</span>
         
         <!-- Desktop Page Jump -->
         <div class="relative">
             <button type="button" @click="togglePageSelector" class="flex items-center gap-1 hover:text-blue-500 transition-colors border border-gray-300 dark:border-gray-600 rounded px-2 py-0.5 bg-gray-50 dark:bg-gray-800 shadow-sm">
                  <span>{{ currentPageRel }} / {{ totalPagesRel }}</span>
             </button>
             <!-- Popover -->
             <div v-if="showPageSelector" class="absolute top-8 right-0 w-40 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden z-[70]">
               <div class="max-h-48 overflow-y-auto p-2">
                   <div class="grid grid-cols-4 gap-2">
                       <button v-for="n in totalPagesRel" :key="n" @click="scrollToPage(n)" 
                           class="p-1 text-xs rounded hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors"
                           :class="{ 'bg-blue-500 text-white': n === currentPageRel }">
                           {{ n }}
                       </button>
                   </div>
               </div>
            </div>
            <!-- Backdrop -->
            <div v-if="showPageSelector" class="fixed inset-0 z-[65] cursor-default" @click="showPageSelector = false"></div>
         </div>
         
         <span class="whitespace-nowrap">{{ wordCount }} 字</span>
      </div>

    </div>

    <!-- Unified Hide/Show Button (Mobile Only) -->
    <!-- Position: isToolbarVisible ? '43px' : '0px' -->
    <!-- Since toolbar is fixed bottom-0 (without JS offset), the toggle sits on top of it. -->
    <div v-if="isMobile"
         class="fixed right-4 z-[51] w-12 h-6 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md rounded-[50%_50%_0_0] flex justify-center items-center cursor-pointer shadow-[0_-1px_3px_rgba(0,0,0,0.05)] border-t border-x border-gray-200 dark:border-gray-700 pointer-events-auto transition-all duration-100 ease-out"
         :style="{ bottom: isToolbarVisible ? '43px' : '0px' }"
         @click.stop.prevent="isToolbarVisible = !isToolbarVisible">
         <!-- Icon rotates based on visibility -->
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="14" 
            height="14" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            stroke-width="2" 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            class="text-gray-500 dark:text-gray-400 transition-transform duration-300"
            :class="{ 'rotate-180': !isToolbarVisible }"
          >
            <path d="m6 9 6 6 6-6"/>
         </svg>
    </div>
    
    <!-- Editor Content Area -->
    <div class="flex-grow bg-white dark:bg-gray-800 rounded-b-lg overflow-y-auto" ref="editorContainerRef" @scroll="handleEditorScroll">
      <editor-content :editor="editor" :class="['min-h-[50vh] p-4 pt-4', isMobile ? 'pb-24' : 'pb-4']" /> 
    </div>
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import Image from "@tiptap/extension-image";
import apiClient from '../api/axios';
import { TextStyle } from '@tiptap/extension-text-style';
import { Extension, Node, mergeAttributes } from '@tiptap/core';
import { TextSelection } from 'prosemirror-state';


const insertPageBreak = () => {
    if (editor.value) {
        editor.value.chain()
            .focus()
            .insertContent({ type: 'pageBreak' })
            .command(({ tr, dispatch, state }) => {
                if (dispatch) {
                     const paragraph = state.schema.nodes.paragraph.create();
                     const insertPos = tr.selection.to;
                     tr.insert(insertPos, paragraph);
                     
                     // Move cursor into the new paragraph (position + 1)
                     const resolvePos = tr.doc.resolve(insertPos + 1);
                     tr.setSelection(TextSelection.near(resolvePos));
                     tr.scrollIntoView();
                }
                return true;
            })
            .run();
    }
};
import { watch, ref, onMounted, onUnmounted, computed, nextTick } from 'vue';

// New Extensions
import Placeholder from '@tiptap/extension-placeholder';
import TextAlign from '@tiptap/extension-text-align';
import Highlight from '@tiptap/extension-highlight';
import CharacterCount from '@tiptap/extension-character-count';

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    fontSize: {
      setFontSize: (size: string) => ReturnType;
      unsetFontSize: () => ReturnType;
    }
    pageBreak: {
        setPageBreak: () => ReturnType;
    }
  }
}

// === Custom Extensions ===

const PageBreak = Node.create({
    name: 'pageBreak',
    group: 'block',
    atom: true,

    addOptions() {
        return {
            HTMLAttributes: {
                class: 'page-break-marker',
                'data-type': 'page-break',
            },
        }
    },

    parseHTML() {
        return [
            { tag: 'hr[data-type="page-break"]' },
        ]
    },

    renderHTML({ HTMLAttributes }) {
        return ['hr', mergeAttributes(this.options.HTMLAttributes, HTMLAttributes)]
    },

     addCommands() {
        return {
            setPageBreak: () => ({ chain }) => {
                return chain().insertContent({ type: this.name }).run()
            },
        }
    },
});

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

const props = defineProps({ 
    modelValue: String, 
    placeholder: String,
    lastSaved: Object as () => Date | null
});
const emit = defineEmits(['update:modelValue']);

// === Reactive State ===
const isMobile = ref(false);
const isFocused = ref(false);
const isToolbarVisible = ref(true); // Default visible
const currentFontSizeIndex = ref(0);
const fontSizes = ['14px', '18px', '24px'];
const fontSizeLabels = ['小', '中', '大'];

// Page & Status Logic
const editorContainerRef = ref<HTMLElement | null>(null);
const currentPageRel = ref(1);
const totalPagesRel = ref(1);
const showPageSelector = ref(false);
const wordCount = ref(0);
const lastSavedTimeStr = ref('');

const currentFontSizeLabel = computed(() => fontSizeLabels[currentFontSizeIndex.value]);

// === Responsiveness Logic ===
const checkMobile = () => {
    isMobile.value = window.innerWidth < 768; 
};

// === Editor Setup ===
const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit.configure({
        heading: false, 
        bulletList: false, 
        orderedList: false,
    }),
    Image,
    TextStyle,
    FontSize as any,
    Highlight,
    PageBreak,
    TextAlign.configure({
      types: ['heading', 'paragraph'],
    }),
    Placeholder.configure({
      placeholder: props.placeholder || '請在此輸入內容...',
    }),
    CharacterCount,
  ],
  editorProps: {
    attributes: {
      class: 'prose dark:prose-invert max-w-none focus:outline-none min-h-[50vh]',
    },
  },
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML());
    updateFontSizeState(editor);
    calculatePageInfo();
    wordCount.value = editor.storage.characterCount.characters();
  },
  onSelectionUpdate: ({ editor }) => {
      updateFontSizeState(editor);
      calculateCurrentPage(); 
  },
  onFocus: () => {
    isFocused.value = true;
  },
  onBlur: () => {
      isFocused.value = false;
  }
});

watch(() => props.modelValue, (newValue) => {
  // CRITICAL FIX: If focused, do not accept external updates to prevent IME interruption
  if (isFocused.value) return; 

  if (editor.value && editor.value.getHTML() !== newValue) {
    editor.value.commands.setContent(newValue || '', { emitUpdate: false });
    nextTick(() => {
        calculatePageInfo();
        if (editor.value) wordCount.value = editor.value.storage.characterCount.characters();
    });
  }
}, { immediate: true });

// Update Time Ago
setInterval(() => {
    if (!props.lastSaved) {
        lastSavedTimeStr.value = '';
        return;
    }
    const diff = Math.floor((new Date().getTime() - props.lastSaved.getTime()) / 1000);
    if (diff < 60) {
        lastSavedTimeStr.value = `${diff}秒鐘前`;
    } else {
        lastSavedTimeStr.value = `${Math.floor(diff / 60)}分鐘前`;
    }
}, 1000);


// === Helper Functions ===

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
  input.value = '';
};

const updateFontSizeState = (ed: any) => {
    const marks = ed.getAttributes('textStyle');
    const size = marks.fontSize;
    if (size) {
        const idx = fontSizes.indexOf(size + 'px');
        if (idx !== -1) currentFontSizeIndex.value = idx;
    }
};

const cycleFontSize = () => {
    currentFontSizeIndex.value = (currentFontSizeIndex.value + 1) % fontSizes.length;
    const size = fontSizes[currentFontSizeIndex.value];
    editor.value?.chain().focus().setFontSize(size).run();
};



// === Page Navigation Logic ===
const hasManualBreaks = computed(() => {
    if (!editor.value) return false;
    let found = false;
    editor.value.state.doc.descendants((node) => {
        if (node.type.name === 'pageBreak') found = true;
        return !found; 
    });
    return found;
});

const calculatePageInfo = () => {
    if (!editor.value) return;
    
    if (hasManualBreaks.value) {
        let breaks = 0;
        editor.value.state.doc.descendants((node) => {
            if (node.type.name === 'pageBreak') breaks++;
        });
        totalPagesRel.value = breaks + 1; // n breaks = n+1 pages
    } else {
        // Auto mode (paragraph count)
        const pCount = editor.value.state.doc.childCount; // Top level blocks
        totalPagesRel.value = Math.max(1, Math.ceil(pCount / 30));
    }
    calculateCurrentPage();
};

const calculateCurrentPage = () => {
    if (!editor.value) return;
    const selParams = editor.value.state.selection;
    const $pos = selParams.$head;
    const pos = $pos.pos;

    if (hasManualBreaks.value) {
        let page = 1;
        editor.value.state.doc.descendants((node, posAt) => {
            if (node.type.name === 'pageBreak' && posAt < pos) {
                page++;
            }
        });
        currentPageRel.value = page;
    } else {
        const index = $pos.index(0); 
        currentPageRel.value = Math.floor(index / 30) + 1;
    }
};

const togglePageSelector = () => {
    showPageSelector.value = !showPageSelector.value;
};

const scrollToPage = (page: number) => {
    if (!editor.value) return;
    showPageSelector.value = false;
    
    let targetPos = 0;
    
    if (hasManualBreaks.value) {
        if (page === 1) targetPos = 0;
        else {
            let breaksFound = 0;
             editor.value.state.doc.descendants((node, pos) => {
                if (node.type.name === 'pageBreak') {
                    breaksFound++;
                    if (breaksFound === page - 1) {
                         targetPos = pos + node.nodeSize;
                         return false; 
                    }
                }
                return true;
            });
        }
    } else {
        const targetIndex = (page - 1) * 30;
        if (targetIndex === 0) targetPos = 0;
        else {
             try {
                let i = 0;
                editor.value.state.doc.forEach((_node, offset) => {
                     if (i === targetIndex) {
                         targetPos = offset; 
                     }
                     i++;
                });
             } catch (e) {}
        }
    }
    
    editor.value.chain().focus().setTextSelection(targetPos).run();
    
    const dom = editor.value.view.domAtPos(targetPos).node as HTMLElement;
    
    // Improved Scrolling Logic
    // Try to find the nearest element because domAtPos might return a text node which doesn't have scrollIntoView
    let elToScroll = dom;
    if (elToScroll && elToScroll.nodeType === 3) { // Text node
         elToScroll = elToScroll.parentElement as HTMLElement;
    }
    
    if (elToScroll && elToScroll.scrollIntoView) {
        elToScroll.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
};

const handleEditorScroll = () => {
};

// === Lifecycle ===
onMounted(() => {
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    // Dynamic Meta Tag for Mobile Editor
    if (isMobile.value) {
        const viewportMeta = document.querySelector('meta[name="viewport"]');
        if (viewportMeta) {
            viewportMeta.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, interactive-widget=resizes-content');
        }
    }
});

onUnmounted(() => {
    window.removeEventListener('resize', checkMobile);
    
    // Revert Meta Tag
    const viewportMeta = document.querySelector('meta[name="viewport"]');
    if (viewportMeta) {
        viewportMeta.setAttribute('content', 'width=device-width, initial-scale=1.0');
    }
});

</script>

<style scoped>
.btn-editor {
  @apply p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors flex items-center justify-center min-w-[32px] min-h-[32px];
}
.is-active {
  @apply bg-blue-100 text-blue-600 dark:bg-gray-700 dark:text-blue-400;
}
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
:deep(.ProseMirror) {
    counter-reset: page-counter;
}
.ProseMirror p.is-editor-empty:first-child::before {
  color: #adb5bd;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}

:deep(.page-break-marker) {
    border: none;
    margin: 2.5rem 0;
    position: relative;
    cursor: default;
    height: 1px;
    background-color: transparent;
    overflow: visible;
    counter-increment: page-counter; /* Increment counter */
}

/* The Line */
:deep(.page-break-marker)::before {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 1px;
    background-color: #e5e7eb;
}

/* The Badge */
:deep(.page-break-marker)::after {
    content: "以上為第 " counter(page-counter) " 頁"; /* Dynamic Content */
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    background: #f3f4f6;
    color: #6b7280;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 500;
    border-radius: 9999px;
    border: 1px solid #d1d5db;
    white-space: nowrap;
    z-index: 10;
}

/* Dark Mode */
:deep(.dark .page-break-marker)::before {
    background-color: #374151;
}
:deep(.dark .page-break-marker)::after {
    background: #1f2937;
    color: #9ca3af;
    border-color: #374151;
}
</style>
