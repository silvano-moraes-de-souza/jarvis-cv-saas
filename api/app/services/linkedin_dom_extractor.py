# ================================================================
# JARVIS CV
# ARQUIVO: linkedin_dom_extractor.py
# DESCRIÇÃO: Extrator de dados LinkedIn via JavaScript (DOM scraping)
# USO: Executar no console do navegador na página do perfil LinkedIn
# ================================================================

DOM_EXTRACT_PROFILE = """
(() => {
  const data = {};

  // Extrair Headline
  const headlineEl = document.querySelector('.text-body-medium, [data-field="headline"]');
  data.headline = headlineEl ? headlineEl.innerText.trim() : '';

  // Extrair About
  const aboutSection = document.querySelector('#about-section, section[id*="about"]');
  data.about = aboutSection ? aboutSection.innerText.trim() : '';

  // Se about não encontrado, tentar alternativa
  if (!data.about) {
    const allText = document.body.innerText;
    const aboutMatch = allText.match(/Sobre\\n([\\s\\S]*?)(?:Experiência|Atividade|Competências)/);
    if (aboutMatch) data.about = aboutMatch[1].trim();
  }

  // Extrair Experience
  const expSection = document.querySelector('#experience-section, section[id*="experience"]');
  data.experience = expSection ? expSection.innerText.trim() : '';

  // Se experience não encontrado, tentar alternativa
  if (!data.experience) {
    const allText = document.body.innerText;
    const expMatch = allText.match(/Experiência([\\s\\S]*?)(?:Formação|Competências|Idiomas)/);
    if (expMatch) data.experience = expMatch[1].trim();
  }

  // Extrair nome
  const nameEl = document.querySelector('h1, .text-heading-xlarge');
  data.name = nameEl ? nameEl.innerText.trim() : '';

  return data;
})();
"""

DOM_EXTRACT_SKILLS = """
(() => {
  const skills = [];

  // Clicar em "Competências" na sidebar se não estiver na página
  const skillsLink = document.querySelector('a[href*="skills"], a[href*="competências"]');
  if (skillsLink) {
    skillsLink.click();
    return { navigating: true };
  }

  // Aguardar conteúdo carregar e extrair skills
  const skillItems = document.querySelectorAll('[data-field="skill-card"], .artdeco-list__item, li.profile-skill');
  skillItems.forEach(item => {
    const nameEl = item.querySelector('.pv-skill-category-entity__name, [aria-label], h3');
    if (nameEl) {
      skills.push(nameEl.innerText.trim());
    }
  });

  // Fallback: buscar qualquer texto que pareça skill
  if (skills.length === 0) {
    const allElements = document.querySelectorAll('span, a, li');
    const skillKeywords = ['python', 'sql', 'power bi', 'excel', 'javascript', 'react', 'data', 'análise', 'gestão'];
    allElements.forEach(el => {
      const text = el.innerText.trim();
      if (text.length > 2 && text.length < 50 && skillKeywords.some(kw => text.toLowerCase().includes(kw))) {
        skills.push(text);
      }
    });
  }

  return { skills: [...new Set(skills)] };
})();
"""

DOM_EXTRACT_ALL_WITH_SKILLS = """
(async () => {
  const data = {};

  // 1. Extrair dados básicos
  const headlineEl = document.querySelector('.text-body-medium, [data-field="headline"]');
  data.headline = headlineEl ? headlineEl.innerText.trim() : '';

  const aboutSection = document.querySelector('section[id*="about"], div[id*="about"]');
  data.about = aboutSection ? aboutSection.innerText.trim() : '';

  const expSection = document.querySelector('section[id*="experience"], div[id*="experience"]');
  data.experience = expSection ? expSection.innerText.trim() : '';

  const nameEl = document.querySelector('h1, .text-heading-xlarge');
  data.name = nameEl ? nameEl.innerText.trim() : '';

  // 2. Navegar para skills
  const skillsLink = Array.from(document.querySelectorAll('a')).find(a =>
    a.href && (a.href.includes('/details/skills/') || a.href.includes('/skills/'))
  );

  if (skillsLink) {
    skillsLink.click();
    await new Promise(r => setTimeout(r, 3000));

    // Extrair skills após navegação
    const allText = document.body.innerText;
    const skillLines = allText.split('\\n').filter(line => {
      const l = line.trim();
      return l.length > 2 && l.length < 60 &&
        !l.includes('Editar') &&
        !l.includes('Competência') &&
        !l.includes('LinkedIn') &&
        !l.includes('Exibido') &&
        !l.match(/^(Todos|Conhecimento|Ferramentas|Competências)$/);
    });

    data.skills = [...new Set(skillLines.slice(0, 50))];
  }

  return data;
})();
"""
