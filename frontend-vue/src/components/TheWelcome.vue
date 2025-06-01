<script setup>
import WelcomeItem from './WelcomeItem.vue'
import DocumentationIcon from './icons/IconDocumentation.vue'
import ToolingIcon from './icons/IconTooling.vue'
import EcosystemIcon from './icons/IconEcosystem.vue'
import CommunityIcon from './icons/IconCommunity.vue'
import SupportIcon from './icons/IconSupport.vue'

const openReadmeInEditor = () => fetch('/__open-in-editor?file=README.md')
</script>

<template>
  <WelcomeItem>
    <template #icon>
      <DocumentationIcon />
    </template>
    <template #heading>Tài liệu</template>

    <a href="https://vuejs.org/" target="_blank" rel="noopener">Tài liệu chính thức</a>
    của Vue cung cấp cho bạn tất cả thông tin cần thiết để bắt đầu.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <ToolingIcon />
    </template>
    <template #heading>Công cụ</template>

    Dự án này được phục vụ và đóng gói với
    <a href="https://vite.dev/guide/features.html" target="_blank" rel="noopener">Vite</a>. Thiết lập IDE được khuyến nghị là
    <a href="https://code.visualstudio.com/" target="_blank" rel="noopener">VSCode</a>
    +
    <a href="https://github.com/vuejs/language-tools" target="_blank" rel="noopener">Vue - Official</a>. Nếu
    bạn cần kiểm tra các thành phần và trang web của mình, hãy thử
    <a href="https://vitest.dev/" target="_blank" rel="noopener">Vitest</a>
    và
    <a href="https://www.cypress.io/" target="_blank" rel="noopener">Cypress</a>
    /
    <a href="https://playwright.dev/" target="_blank" rel="noopener">Playwright</a>.

    <br />

    Thêm hướng dẫn có sẵn trong
    <a href="javascript:void(0)" @click="openReadmeInEditor"><code>README.md</code></a
    >.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <EcosystemIcon />
    </template>
    <template #heading>Hệ sinh thái</template>

    Nhận các công cụ và thư viện chính thức cho dự án của bạn:
    <a href="https://pinia.vuejs.org/" target="_blank" rel="noopener">Pinia</a>,
    <a href="https://router.vuejs.org/" target="_blank" rel="noopener">Vue Router</a>,
    <a href="https://test-utils.vuejs.org/" target="_blank" rel="noopener">Vue Test Utils</a>, và
    <a href="https://github.com/vuejs/devtools" target="_blank" rel="noopener">Vue Dev Tools</a>. Nếu
    bạn cần thêm tài nguyên, chúng tôi đề xuất bạn tham khảo
    <a href="https://github.com/vuejs/awesome-vue" target="_blank" rel="noopener">Awesome Vue</a>.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <CommunityIcon />
    </template>
    <template #heading>Cộng đồng</template>

    Gặp khó khăn? Đặt câu hỏi của bạn trên
    <a href="https://chat.vuejs.org" target="_blank" rel="noopener">Vue Land</a>
    (máy chủ Discord chính thức của chúng tôi), hoặc
    <a href="https://stackoverflow.com/questions/tagged/vue.js" target="_blank" rel="noopener"
      >StackOverflow</a
    >. Bạn cũng nên theo dõi
    <a href="https://bsky.app/profile/vuejs.org" target="_blank" rel="noopener">@vuejs.org</a>
    trên Bluesky hoặc
    <a href="https://x.com/vuejs" target="_blank" rel="noopener">@vuejs</a>
    trên X để cập nhật tin tức mới nhất trong thế giới Vue.
  </WelcomeItem>

  <WelcomeItem>
    <template #icon>
      <SupportIcon />
    </template>
    <template #heading>Hỗ trợ Vue</template>

    Là một dự án độc lập, Vue phụ thuộc vào sự hỗ trợ của cộng đồng để duy trì. Bạn có thể giúp
    chúng tôi bằng cách
    <a href="https://vuejs.org/sponsor/" target="_blank" rel="noopener">trở thành nhà tài trợ</a>.
  </WelcomeItem>
</template>
