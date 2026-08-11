const fallbackSlides = [
  {
    title: "Trusted Financial Growth",
    image: "/static/banner1.png",
  },
  {
    title: "Member First Approach",
    image: "/static/banner2.png",
  },
  {
    title: "Reliable Partnership",
    image: "/static/banner3.png",
  },
  {
    title: "Community Financial Support",
    image: "/static/banner4.png",
  },
  {
    title: "Secure Savings Services",
    image: "/static/banner5.png",
  },
  {
    title: "Growing Together",
    image: "/static/banner6.png",
  },
];

const services = [
  {
    title: "बचत सेवा (Saving Services)",
    description: "विभिन्न प्रकारका बचत योजनाहरुमा सुरक्षित बचत गर्ने सुविधा ।",
    image: "/static/Saving Services1.png",
  },
  {
    title: "मुद्रती निक्षेप (Fixed Deposit)",
    description: "आकर्षक ब्याजदरमा निश्चित अवधिका लागि निक्षेप राख्ने सुविधा ।",
    image: "/static/fixed deposit2.png",
  },
  {
    title: "कर्जा सेवा (Loan Services)",
    description:
      "व्यवसाय, शिक्षा, घर, उपभोग लगायतका आवश्यकताका लागि कर्जा सुविधा ।",
    image: "/static/loan services3.png",
  },
  {
    title: "समूह बचत (Group Saving)",
    description:
      "समूहमा आबद्ध भई संयुक्त रुपमा बचत गर्ने सुविधा तथा प्रोत्साहन ।",
    image: "/static/group serivces4.png",
  },
];

const fallbackContent = {
  banners: fallbackSlides,

  news: [
    {
      title: "Latest cooperative updates will appear here",
      description:
        "Add news and activity posts from Django admin to show them on the homepage.",
      published_at: "Latest",
    },
  ],

  notices: [
    {
      title: "Member notices will appear here",
      description:
        "Add active notices from Django admin with optional documents.",
      published_at: "Notice",
    },
  ],

  downloads: [
    {
      title: "Download documents will appear here",
      description:
        "Upload forms, policies, reports, or other files from Django admin.",
      published_at: "Download",
    },
  ],

  popup: null,
};

export { fallbackSlides, services, fallbackContent };
