import { ref, reactive } from "vue";

export const CATEGORY_OPTIONS = [
  { label: '政务', value: '政务' },
  { label: '医疗', value: '医疗' },
  { label: '教育', value: '教育' },
  { label: '文化', value: '文化' },
  { label: '交通', value: '交通' },
  { label: '生活', value: '生活' }
]

export const selectedCategory = ref('')

export const editDialogView = ref(false)
export const editForm = reactive({
  id: null,
  name: '',
  category: '',
  address: '',
  phone: '',
  tags: '',
  description: '',
  status: 0
})
