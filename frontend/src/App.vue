<script setup>
import { nextTick, ref } from 'vue'
import {
  Bot,
  CheckCircle2,
  FileText,
  LoaderCircle,
  RotateCcw,
  Send,
  Upload,
  User,
  X,
} from 'lucide-vue-next'

import {
  askQuestion,
  uploadDocument,
} from './services/api'

const selectedFile = ref(null)
const uploadResult = ref(null)
const uploading = ref(false)
const answering = ref(false)
const errorMessage = ref('')
const chatError = ref('')
const question = ref('')
const messages = ref([])
const messageList = ref(null)

const allowedExtensions = ['pdf', 'txt', 'png', 'jpg', 'jpeg']
const maximumFileSize = 10 * 1024 * 1024

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} bytes`

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function selectFile(file) {
  errorMessage.value = ''
  uploadResult.value = null
  messages.value = []

  if (!file) return

  const extension = file.name.split('.').pop()?.toLowerCase()

  if (!allowedExtensions.includes(extension)) {
    errorMessage.value =
      'Please select a PDF, TXT, PNG, JPG, or JPEG file.'
    selectedFile.value = null
    return
  }

  if (file.size > maximumFileSize) {
    errorMessage.value = 'The file must be smaller than 10 MB.'
    selectedFile.value = null
    return
  }

  selectedFile.value = file
}

function handleFileInput(event) {
  selectFile(event.target.files?.[0])
  event.target.value = ''
}

function handleDrop(event) {
  selectFile(event.dataTransfer.files?.[0])
}

function resetDocument() {
  selectedFile.value = null
  uploadResult.value = null
  errorMessage.value = ''
  chatError.value = ''
  question.value = ''
  messages.value = []
}

async function scrollToLatestMessage() {
  await nextTick()

  if (messageList.value) {
    messageList.value.scrollTop =
      messageList.value.scrollHeight
  }
}

async function submitUpload() {
  if (!selectedFile.value || uploading.value) return

  uploading.value = true
  errorMessage.value = ''

  try {
    uploadResult.value = await uploadDocument(selectedFile.value)

    messages.value = [
      {
        role: 'assistant',
        content: 'Document ready.',
        sources: [],
      },
    ]
  } catch (error) {
    errorMessage.value =
      error.response?.data?.detail ||
      'The document could not be uploaded. Please try again.'
  } finally {
    uploading.value = false
  }
}

async function submitQuestion() {
  const currentQuestion = question.value.trim()

  if (
    !currentQuestion ||
    !uploadResult.value ||
    answering.value
  ) {
    return
  }

  messages.value.push({
    role: 'user',
    content: currentQuestion,
    sources: [],
  })

  question.value = ''
  chatError.value = ''
  answering.value = true

  await scrollToLatestMessage()

  try {
    const response = await askQuestion({
      documentId: uploadResult.value.document_id,
      sessionId: uploadResult.value.session_id,
      question: currentQuestion,
    })

    messages.value.push({
      role: 'assistant',
      content: response.answer,
      sources: response.sources,
    })
  } catch (error) {
    messages.value.pop()
    question.value = currentQuestion
    chatError.value =
      error.response?.data?.detail ||
      'The question could not be answered. Please try again.'
  } finally {
    answering.value = false
    await scrollToLatestMessage()
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-950">
    <header class="border-b border-gray-200 bg-white">
      <div class="mx-auto flex h-16 max-w-5xl items-center px-5">
        <FileText class="mr-3 size-6 text-blue-700" />
        <h1 class="text-lg font-semibold">Document Q&amp;A Agent</h1>
      </div>
    </header>

    <main class="mx-auto max-w-5xl px-5 py-8">
      <section v-if="!uploadResult" class="max-w-3xl">
        <h2 class="text-2xl font-semibold">Upload a document</h2>

        <p class="mt-2 text-sm text-gray-600">
          PDF, TXT, PNG, JPG or JPEG, up to 10 MB
        </p>

        <label
          class="mt-6 flex min-h-52 cursor-pointer flex-col items-center justify-center border-2 border-dashed border-gray-300 bg-white px-6 text-center transition hover:border-blue-500 hover:bg-blue-50"
          @dragover.prevent
          @drop.prevent="handleDrop"
        >
          <Upload class="size-9 text-blue-700" />

          <span class="mt-4 font-medium">
            Select or drop a document
          </span>

          <input
            class="sr-only"
            type="file"
            accept=".pdf,.txt,.png,.jpg,.jpeg"
            @change="handleFileInput"
          />
        </label>

        <div
          v-if="selectedFile"
          class="mt-4 flex items-center justify-between border border-gray-200 bg-white p-4"
        >
          <div class="min-w-0">
            <p class="truncate font-medium">
              {{ selectedFile.name }}
            </p>

            <p class="mt-1 text-sm text-gray-500">
              {{ formatFileSize(selectedFile.size) }}
            </p>
          </div>

          <button
            type="button"
            class="ml-4 grid size-9 shrink-0 place-items-center text-gray-500 hover:bg-gray-100 hover:text-gray-900"
            title="Remove selected file"
            @click="resetDocument"
          >
            <X class="size-5" />
          </button>
        </div>

        <p
          v-if="errorMessage"
          class="mt-4 border-l-4 border-red-500 bg-red-50 p-4 text-sm text-red-800"
          role="alert"
        >
          {{ errorMessage }}
        </p>

        <button
          type="button"
          class="mt-5 inline-flex h-11 items-center justify-center bg-blue-700 px-5 font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-gray-400"
          :disabled="!selectedFile || uploading"
          @click="submitUpload"
        >
          <LoaderCircle
            v-if="uploading"
            class="mr-2 size-5 animate-spin"
          />

          <Upload v-else class="mr-2 size-5" />

          {{ uploading ? 'Processing document...' : 'Upload document' }}
        </button>
      </section>

      <section v-else>
        <div
          class="flex flex-wrap items-center justify-between gap-4 border-b border-gray-200 pb-5"
        >
          <div class="flex min-w-0 items-center">
            <CheckCircle2 class="mr-3 size-5 shrink-0 text-green-700" />

            <div class="min-w-0">
              <p class="truncate font-medium">
                {{ uploadResult.filename }}
              </p>

              <p class="mt-1 text-sm text-gray-500">
                {{ uploadResult.chunks_stored }} chunk(s) indexed
              </p>
            </div>
          </div>

          <button
            type="button"
            class="inline-flex h-10 items-center border border-gray-300 bg-white px-4 text-sm font-medium hover:bg-gray-100"
            @click="resetDocument"
          >
            <RotateCcw class="mr-2 size-4" />
            New document
          </button>
        </div>

        <div
          ref="messageList"
          class="mt-6 h-[480px] overflow-y-auto border border-gray-200 bg-white p-5"
          aria-live="polite"
        >
          <div
            v-for="(message, index) in messages"
            :key="index"
            class="mb-6 flex items-start last:mb-0"
          >
            <div
              class="mr-3 grid size-9 shrink-0 place-items-center"
              :class="
                message.role === 'user'
                  ? 'bg-gray-900 text-white'
                  : 'bg-blue-100 text-blue-800'
              "
            >
              <User
                v-if="message.role === 'user'"
                class="size-5"
              />
              <Bot v-else class="size-5" />
            </div>

            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold">
                {{ message.role === 'user' ? 'You' : 'Assistant' }}
              </p>

              <p class="mt-1 whitespace-pre-wrap text-sm leading-6 text-gray-700">
                {{ message.content }}
              </p>

            </div>
          </div>

          <div
            v-if="answering"
            class="flex items-center text-sm text-gray-500"
          >
            <LoaderCircle class="mr-2 size-4 animate-spin" />
            Generating answer...
          </div>
        </div>

        <p
          v-if="chatError"
          class="mt-4 border-l-4 border-red-500 bg-red-50 p-4 text-sm text-red-800"
          role="alert"
        >
          {{ chatError }}
        </p>

        <form
          class="mt-4 flex gap-3"
          @submit.prevent="submitQuestion"
        >
          <input
            v-model="question"
            type="text"
            class="h-11 min-w-0 flex-1 border border-gray-300 bg-white px-4 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
            placeholder="Ask a question about the document"
            maxlength="1000"
            :disabled="answering"
          />

          <button
            type="submit"
            class="inline-flex h-11 items-center justify-center bg-blue-700 px-5 font-medium text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-gray-400"
            :disabled="!question.trim() || answering"
          >
            <Send class="mr-2 size-5" />
            Ask
          </button>
        </form>
      </section>
    </main>
  </div>
</template>
